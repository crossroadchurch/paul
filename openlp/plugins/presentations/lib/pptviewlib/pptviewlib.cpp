/******************************************************************************
* OpenLP - Open Source Lyrics Projection                                      *
* --------------------------------------------------------------------------- *
* Copyright (c) 2008-2015 OpenLP Developers                                   *
* --------------------------------------------------------------------------- *
* This program is free software; you can redistribute it and/or modify it     *
* under the terms of the GNU General Public License as published by the Free  *
* Software Foundation; version 2 of the License.                              *
*                                                                             *
* This program is distributed in the hope that it will be useful, but WITHOUT *
* ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       *
* FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for    *
* more details.                                                               *
*                                                                             *
* You should have received a copy of the GNU General Public License along     *
* with this program; if not, write to the Free Software Foundation, Inc., 59  *
* Temple Place, Suite 330, Boston, MA 02111-1307 USA                          *
******************************************************************************/

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <io.h>
#include <direct.h>
#include <time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include "pptviewlib.h"

// Because of the callbacks used by SetWindowsHookEx, the memory used needs to
// be sharable across processes (the callbacks are done from a different
// process) Therefore use data_seg with RWS memory.
//
// See http://msdn.microsoft.com/en-us/library/aa366551(VS.85).aspx for
// alternative method of holding memory, removing fixed limits which would allow
// dynamic number of items, rather than a fixed number. Use a Local\ mapping,
// since global has UAC issues in Vista.

#pragma data_seg(".PPTVIEWLIB")
PPTVIEW pptView[MAX_PPTS] = {NULL};
HHOOK globalHook = NULL;
BOOL debug = FALSE;
#pragma data_seg()
#pragma comment(linker, "/SECTION:.PPTVIEWLIB,RWS")

HINSTANCE hInstance = NULL;

BOOL APIENTRY DllMain(HMODULE hModule, DWORD  ulReasonForCall,
    LPVOID lpReserved)
{
    hInstance = (HINSTANCE)hModule;
    switch(ulReasonForCall)
    {
        case DLL_PROCESS_ATTACH:
            DEBUG(L"PROCESS_ATTACH\n");
            break;
        case DLL_THREAD_ATTACH:
            //DEBUG(L"THREAD_ATTACH\n");
            break;
        case DLL_THREAD_DETACH:
            //DEBUG(L"THREAD_DETACH\n");
            break;
        case DLL_PROCESS_DETACH:
            // Clean up... hopefully there is only the one process attached?
            // We'll find out soon enough during tests!
            DEBUG(L"PROCESS_DETACH\n");
            for (int i = 0; i < MAX_PPTS; i++)
                ClosePPT(i);
            break;
    }
    return TRUE;
}

DllExport void SetDebug(BOOL onOff)
{
    printf("SetDebug\n");
    debug = onOff;
    DEBUG(L"enabled\n");
}

DllExport BOOL CheckInstalled()
{
    wchar_t cmdLine[MAX_PATH * 2];

    DEBUG(L"CheckInstalled\n");
    BOOL found = GetPPTViewerPath(cmdLine, sizeof(cmdLine));
    if(found)
    {
        DEBUG(L"Exe: %s\n", cmdLine);
    }
    return found;
}

// Open the PointPoint, count the slides and take a snapshot of each slide
// for use in previews
// previewpath is a prefix for the location to put preview images of each slide.
// "<n>.bmp" will be appended to complete the path. E.g. "c:\temp\slide" would
// create "c:\temp\slide1.bmp" slide2.bmp, slide3.bmp etc.
// It will also create a *info.txt containing information about the ppt
DllExport int OpenPPT(wchar_t *filename, HWND hParentWnd, RECT rect,
    wchar_t *previewPath)
{
    STARTUPINFO si;
    PROCESS_INFORMATION pi;
    wchar_t cmdLine[MAX_PATH * 2];
    int id;

    DEBUG(L"OpenPPT start: %s; %s\n", filename, previewPath);
    DEBUG(L"OpenPPT start: %u; %i, %i, %i, %i\n", hParentWnd, rect.top,
        rect.left, rect.bottom, rect.right);
    if (GetPPTViewerPath(cmdLine, sizeof(cmdLine)) == FALSE)
    {
        DEBUG(L"OpenPPT: GetPPTViewerPath failed\n");
        return -1;
    }
    id = -1;
    for (int i = 0; i < MAX_PPTS; i++)
    {
        if (pptView[i].state == PPT_CLOSED)
        {
            id = i;
            break;
        }
    }
    if (id < 0)
    {
        DEBUG(L"OpenPPT: Too many PPTs\n");
        return -1;
    }
    memset(&pptView[id], 0, sizeof(PPTVIEW));
    wcscpy_s(pptView[id].filename, MAX_PATH, filename);
    wcscpy_s(pptView[id].previewPath, MAX_PATH, previewPath);
    pptView[id].state = PPT_CLOSED;
    pptView[id].slideCount = 0;
    pptView[id].currentSlide = 0;
    pptView[id].firstSlideSteps = 0;
    pptView[id].lastSlideSteps = 0;
    pptView[id].guess = 0;
    pptView[id].hParentWnd = hParentWnd;
    pptView[id].hWnd = NULL;
    pptView[id].hWnd2 = NULL;
    for (int i = 0; i < MAX_SLIDES; i++)
    {
        pptView[id].slideNos[i] = 0;
    }
    if (hParentWnd != NULL && rect.top == 0 && rect.bottom == 0
        && rect.left == 0 && rect.right == 0)
    {
        LPRECT windowRect = NULL;
        GetWindowRect(hParentWnd, windowRect);
        pptView[id].rect.top = 0;
        pptView[id].rect.left = 0;
        pptView[id].rect.bottom = windowRect->bottom - windowRect->top;
        pptView[id].rect.right = windowRect->right - windowRect->left;
    }
    else
    {
        pptView[id].rect.top = rect.top;
        pptView[id].rect.left = rect.left;
        pptView[id].rect.bottom = rect.bottom;
        pptView[id].rect.right = rect.right;
    }
    wcscat_s(cmdLine, MAX_PATH * 2, L" /F /S \"");
    wcscat_s(cmdLine, MAX_PATH * 2, filename);
    wcscat_s(cmdLine, MAX_PATH * 2, L"\"");
    memset(&si, 0, sizeof(si));
    memset(&pi, 0, sizeof(pi));
    BOOL gotInfo = GetPPTInfo(id);
    /*
     * I'd really like to just hook on the new threadid. However this always
     * gives error 87. Perhaps I'm hooking to soon? No idea... however can't
     * wait since I need to ensure I pick up the WM_CREATE as this is the only
     * time the window can be resized in such away the content scales correctly
     *
     * hook = SetWindowsHookEx(WH_CBT,CbtProc,hInstance,pi.dwThreadId);
     */
    if (globalHook != NULL)
    {
        UnhookWindowsHookEx(globalHook);
    }
    globalHook = SetWindowsHookEx(WH_CBT, CbtProc, hInstance, NULL);
    if (globalHook == 0)
    {
        DEBUG(L"OpenPPT: SetWindowsHookEx failed\n");
        ClosePPT(id);
        return -1;
    }
    pptView[id].state = PPT_STARTED;
    Sleep(10);
    if (!CreateProcess(NULL, cmdLine, NULL, NULL, FALSE, 0, 0, NULL, &si, &pi))
    {
        DEBUG(L"OpenPPT: CreateProcess failed: %s\n", cmdLine);
        ClosePPT(id);
        return -1;
    }
    pptView[id].dwProcessId = pi.dwProcessId;
    pptView[id].dwThreadId = pi.dwThreadId;
    pptView[id].hThread = pi.hThread;
    pptView[id].hProcess = pi.hProcess;
    while (pptView[id].state == PPT_STARTED)
        Sleep(10);
    if (gotInfo)
    {
        DEBUG(L"OpenPPT: Info loaded, no refresh\n");
        pptView[id].state = PPT_LOADED;
        Resume(id);
    }
    else
    {
        DEBUG(L"OpenPPT: Get info\n");
        pptView[id].steps = 0;
        int steps = 0;
        while (pptView[id].state == PPT_OPENED)
        {
            if (steps <= pptView[id].steps)
            {
                Sleep(100);
                DEBUG(L"OpenPPT: Step %d/%d\n", steps, pptView[id].steps);
                steps++;
                NextStep(id);
            }
            Sleep(10);
        }
        DEBUG(L"OpenPPT: Slides %d, Steps %d, first slide steps %d\n",
            pptView[id].slideCount, pptView[id].steps,
            pptView[id].firstSlideSteps);
        for(int i = 1; i <= pptView[id].slideCount; i++)
        {
            DEBUG(L"OpenPPT: Slide %d = %d\n", i, pptView[id].slideNos[i]);
        }
        SavePPTInfo(id);
        if (pptView[id].state == PPT_CLOSING
            || pptView[id].slideCount <= 0)
        {
            ClosePPT(id);
            id=-1;
        }
        else
        {
               RestartShow(id);
        }
    }
    if (id >= 0)
    {
        if (pptView[id].msgHook != NULL)
        {
            UnhookWindowsHookEx(pptView[id].msgHook);
        }
        pptView[id].msgHook = NULL;
    }
    DEBUG(L"OpenPPT: Exit: id=%i\n", id);
    return id;
}
// Load information about the ppt from an info.txt file.
// Format:
// version
// filedate
// filesize
// slidecount
// first slide steps
BOOL GetPPTInfo(int id)
{
    struct _stat fileStats;
    wchar_t info[MAX_PATH];
    FILE* pFile;
    wchar_t buf[100];

    DEBUG(L"GetPPTInfo: start\n");
    if (_wstat(pptView[id].filename, &fileStats) != 0)
    {
        return FALSE;
    }
    swprintf_s(info, MAX_PATH, L"%sinfo.txt", pptView[id].previewPath);
    int err = _wfopen_s(&pFile, info, L"r");
    if (err != 0)
    {
        DEBUG(L"GetPPTInfo: file open failed - %d\n", err);
        return FALSE;
    }
    fgetws(buf, 100, pFile); // version == 1
    fgetws(buf, 100, pFile);
    if (fileStats.st_mtime != _wtoi(buf))
    {
        DEBUG(L"GetPPTInfo: date changed\n");
        fclose (pFile);
        return FALSE;
    }
    fgetws(buf, 100, pFile);
    if (fileStats.st_size != _wtoi(buf))
    {
        DEBUG(L"GetPPTInfo: size changed\n");
        fclose (pFile);
        return FALSE;
    }
    fgetws(buf, 100, pFile); // slidecount
    int slideCount = _wtoi(buf);
    fgetws(buf, 100, pFile); // first slide steps
    int firstSlideSteps = _wtoi(buf);
    // check all the preview images still exist
    for (int i = 1; i <= slideCount; i++)
    {
        swprintf_s(info, MAX_PATH, L"%s%i.bmp", pptView[id].previewPath, i);
        if (GetFileAttributes(info) == INVALID_FILE_ATTRIBUTES)
        {
            DEBUG(L"GetPPTInfo: bmp not found\n");
            return FALSE;
        }
    }
    fclose(pFile);
    pptView[id].slideCount = slideCount;
    pptView[id].firstSlideSteps = firstSlideSteps;
    DEBUG(L"GetPPTInfo: exit ok\n");
    return TRUE;
}

BOOL SavePPTInfo(int id)
{
    struct _stat fileStats;
    wchar_t info[MAX_PATH];
    FILE* pFile;

    DEBUG(L"SavePPTInfo: start\n");
    if (_wstat(pptView[id].filename, &fileStats) != 0)
    {
        DEBUG(L"SavePPTInfo: stat of %s failed\n", pptView[id].filename);
        return FALSE;
    }
    swprintf_s(info, MAX_PATH, L"%sinfo.txt", pptView[id].previewPath);
    int err = _wfopen_s(&pFile, info, L"w");
    if (err != 0)
    {
        DEBUG(L"SavePPTInfo: fopen of %s failed%i\n", info, err);
        return FALSE;
    }
    fprintf(pFile, "1\n");
    fprintf(pFile, "%u\n", fileStats.st_mtime);
    fprintf(pFile, "%u\n", fileStats.st_size);
    fprintf(pFile, "%u\n", pptView[id].slideCount);
    fprintf(pFile, "%u\n", pptView[id].firstSlideSteps);
    fclose(pFile);
    DEBUG(L"SavePPTInfo: exit ok\n");
    return TRUE;
}

// Get the path of the PowerPoint viewer from the registry
BOOL GetPPTViewerPath(wchar_t *pptViewerPath, int stringSize)
{
    wchar_t cwd[MAX_PATH];

    DEBUG(L"GetPPTViewerPath: start\n");
    if(GetPPTViewerPathFromReg(pptViewerPath, stringSize))
    {
        if(_waccess(pptViewerPath, 0) != -1)
        {
            DEBUG(L"GetPPTViewerPath: exit registry\n");
            return TRUE;
        }
    }
    // This is where it gets ugly. PPT2007 it seems no longer stores its
    // location in the registry. So we have to use the defaults which will
    // upset those who like to put things somewhere else

    // Viewer 2007 in 64bit Windows:
    if(_waccess(L"C:\\Program Files (x86)\\Microsoft Office\\Office12\\PPTVIEW.EXE",
        0) != -1)
    {
        wcscpy_s(
            L"C:\\Program Files (x86)\\Microsoft Office\\Office12\\PPTVIEW.EXE",
            stringSize, pptViewerPath);
        DEBUG(L"GetPPTViewerPath: exit 64bit 2007\n");
        return TRUE;
    }
    // Viewer 2007 in 32bit Windows:
    if(_waccess(L"C:\\Program Files\\Microsoft Office\\Office12\\PPTVIEW.EXE", 0)
        != -1)
    {
        wcscpy_s(L"C:\\Program Files\\Microsoft Office\\Office12\\PPTVIEW.EXE",
            stringSize, pptViewerPath);
        DEBUG(L"GetPPTViewerPath: exit 32bit 2007\n");
        return TRUE;
    }
    // Give them the opportunity to place it in the same folder as the app
    _wgetcwd(cwd, MAX_PATH);
    wcscat_s(cwd, MAX_PATH, L"\\PPTVIEW.EXE");
    if(_waccess(cwd, 0) != -1)
    {
        wcscpy_s(pptViewerPath, stringSize, cwd);
        DEBUG(L"GetPPTViewerPath: exit local\n");
        return TRUE;
    }
    DEBUG(L"GetPPTViewerPath: exit fail\n");
    return FALSE;
}
BOOL GetPPTViewerPathFromReg(wchar_t *pptViewerPath, int stringSize)
{
    HKEY hKey;
    DWORD dwType, dwSize;
    LRESULT lResult;

    // The following registry settings are for, respectively, (I think)
    // PPT Viewer 2007 (older versions. Latest not in registry) & PPT Viewer 2010
    // PPT Viewer 2003 (recent versions)
    // PPT Viewer 2003 (older versions) 
    // PPT Viewer 97
    if ((RegOpenKeyExW(HKEY_CLASSES_ROOT,
        L"PowerPointViewer.Show.12\\shell\\Show\\command", 0, KEY_READ, &hKey)
        != ERROR_SUCCESS)
        && (RegOpenKeyExW(HKEY_CLASSES_ROOT,
        L"PowerPointViewer.Show.11\\shell\\Show\\command", 0, KEY_READ, &hKey)
        != ERROR_SUCCESS)
        && (RegOpenKeyExW(HKEY_CLASSES_ROOT,
        L"Applications\\PPTVIEW.EXE\\shell\\open\\command", 0, KEY_READ, &hKey)
        != ERROR_SUCCESS)
        && (RegOpenKeyExW(HKEY_CLASSES_ROOT,
        L"Applications\\PPTVIEW.EXE\\shell\\Show\\command", 0, KEY_READ, &hKey)
        != ERROR_SUCCESS))
    {
        return FALSE;
    }
    dwType = REG_SZ;
    dwSize = (DWORD)stringSize;
    lResult = RegQueryValueEx(hKey, NULL, NULL, &dwType, (LPBYTE)pptViewerPath,
        &dwSize);
    RegCloseKey(hKey);
    if (lResult != ERROR_SUCCESS)
    {
        return FALSE;
    }
    // remove "%1" from end of key value
    pptViewerPath[wcslen(pptViewerPath) - 4] = '\0';
    return TRUE;
}

// Unhook the Windows hook
void Unhook(int id)
{
    DEBUG(L"Unhook: start %d\n", id);
    if (pptView[id].hook != NULL)
    {
        UnhookWindowsHookEx(pptView[id].hook);
    }
    if (pptView[id].msgHook != NULL)
    {
        UnhookWindowsHookEx(pptView[id].msgHook);
    }
    pptView[id].hook = NULL;
    pptView[id].msgHook = NULL;
    DEBUG(L"Unhook: exit ok\n");
}

// Close the PowerPoint viewer, release resources
DllExport void ClosePPT(int id)
{
    DEBUG(L"ClosePPT: start%d\n", id);
    pptView[id].state = PPT_CLOSED;
    Unhook(id);
    if (pptView[id].hWnd == 0)
    {
        TerminateThread(pptView[id].hThread, 0);
    }
    else
    {
        PostMessage(pptView[id].hWnd, WM_CLOSE, 0, 0);
    }
    CloseHandle(pptView[id].hThread);
    CloseHandle(pptView[id].hProcess);
    memset(&pptView[id], 0, sizeof(PPTVIEW));
    DEBUG(L"ClosePPT: exit ok\n");
    return;
}
// Moves the show back onto the display
DllExport void Resume(int id)
{
    DEBUG(L"Resume: %d\n", id);
    MoveWindow(pptView[id].hWnd, pptView[id].rect.left,
        pptView[id].rect.top,
        pptView[id].rect.right - pptView[id].rect.left,
        pptView[id].rect.bottom - pptView[id].rect.top, TRUE);
    Unblank(id);
}
// Moves the show off the screen so it can't be seen
DllExport void Stop(int id)
{
    DEBUG(L"Stop:%d\n", id);
    MoveWindow(pptView[id].hWnd, -32000, -32000,
        pptView[id].rect.right - pptView[id].rect.left,
        pptView[id].rect.bottom - pptView[id].rect.top, TRUE);
}

// Return the total number of slides
DllExport int GetSlideCount(int id)
{
    DEBUG(L"GetSlideCount:%d\n", id);
    if (pptView[id].state == 0)
    {
        return -1;
    }
    else
    {
        return pptView[id].slideCount;
    }
}

// Return the number of the slide currently viewing
DllExport int GetCurrentSlide(int id)
{
    DEBUG(L"GetCurrentSlide:%d\n", id);
    if (pptView[id].state == 0)
    {
        return -1;
    }
    else
    {
        return pptView[id].currentSlide;
    }
}

// Take a step forwards through the show
DllExport void NextStep(int id)
{
    DEBUG(L"NextStep:%d (%d)\n", id, pptView[id].currentSlide);
    if (pptView[id].currentSlide > pptView[id].slideCount) return;
    if (pptView[id].currentSlide < pptView[id].slideCount)
    {
        pptView[id].guess = pptView[id].currentSlide + 1;
    }
    PostMessage(pptView[id].hWnd2, WM_MOUSEWHEEL, MAKEWPARAM(0, -WHEEL_DELTA),
        0);
}

// Take a step backwards through the show
DllExport void PrevStep(int id)
{
    DEBUG(L"PrevStep:%d (%d)\n", id, pptView[id].currentSlide);
    if (pptView[id].currentSlide > 1)
    {
        pptView[id].guess = pptView[id].currentSlide - 1;
    }
    PostMessage(pptView[id].hWnd2, WM_MOUSEWHEEL, MAKEWPARAM(0, WHEEL_DELTA),
        0);
}

// Blank the show (black screen)
DllExport void Blank(int id)
{
    // B just toggles blank on/off. However pressing any key unblanks.
    // So send random unmapped letter first (say 'A'), then we can
    // better guarantee B will blank instead of trying to guess
    // whether it was already blank or not.
    DEBUG(L"Blank:%d\n", id);
    HWND h1 = GetForegroundWindow();
    HWND h2 = GetFocus();
    SetForegroundWindow(pptView[id].hWnd);
    SetFocus(pptView[id].hWnd);
    // slight pause, otherwise event triggering this call may grab focus back!
    Sleep(50);
    keybd_event((int)'A', 0, 0, 0);
    keybd_event((int)'A', 0, KEYEVENTF_KEYUP, 0);
    keybd_event((int)'B', 0, 0, 0);
    keybd_event((int)'B', 0, KEYEVENTF_KEYUP, 0);
    SetForegroundWindow(h1);
    SetFocus(h2);
}
// Unblank the show
DllExport void Unblank(int id)
{
    DEBUG(L"Unblank:%d\n", id);
    // Pressing any key resumes.
    // For some reason SendMessage works for unblanking, but not blanking.
    SendMessage(pptView[id].hWnd2, WM_CHAR, 'A', 0);
}

// Go directly to a slide
DllExport void GotoSlide(int id, int slideNo)
{
    DEBUG(L"GotoSlide %i %i:\n", id, slideNo);
    // Did try WM_KEYDOWN/WM_CHAR/WM_KEYUP with SendMessage but didn't work
    // perhaps I was sending to the wrong window? No idea.
    // Anyway fall back to keybd_event, which is OK as long we makesure
    // the slideshow has focus first
    char ch[10];

    if (slideNo < 0) return;
    pptView[id].guess = slideNo;
    _itoa_s(slideNo, ch, 10, 10);
    HWND h1 = GetForegroundWindow();
    HWND h2 = GetFocus();
    SetForegroundWindow(pptView[id].hWnd);
    SetFocus(pptView[id].hWnd);
    // slight pause, otherwise event triggering this call may grab focus back!
    Sleep(50);
    for (int i=0; i<10; i++)
    {
        if (ch[i] == '\0') break;
        keybd_event((BYTE)ch[i], 0, 0, 0);
        keybd_event((BYTE)ch[i], 0, KEYEVENTF_KEYUP, 0);
    }
    keybd_event(VK_RETURN, 0, 0, 0);
    keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0);
    SetForegroundWindow(h1);
    SetFocus(h2);
}

// Restart the show from the beginning
DllExport void RestartShow(int id)
{
    // If we just go direct to slide one, then it remembers that all other
    // slides have been animated, so ends up just showing the completed slides
    // of those slides that have been animated next time we advance.
    // Only way I've found to get around this is to step backwards all the way
    // through. Lets move the window out of the way first so the audience
    // doesn't see this.
    DEBUG(L"RestartShow:%d\n", id);
    Stop(id);
    GotoSlide(id, pptView[id].slideCount);
    for (int i=0; i <= pptView[id].steps - pptView[id].lastSlideSteps; i++)
    {
        PrevStep(id);
        Sleep(10);
    }
    int i = 0;
    while ((pptView[id].currentSlide > 1) && (i++ < 30000))
    {
        Sleep(10);
    }
    Resume(id);
}

// This hook is started with the PPTVIEW.EXE process and waits for the
// WM_CREATEWND message. At this point (and only this point) can the
// window be resized to the correct size.
// Release the hook as soon as we're complete to free up resources
LRESULT CALLBACK CbtProc(int nCode, WPARAM wParam, LPARAM lParam)
{
    HHOOK hook = globalHook;
    if (nCode == HCBT_CREATEWND)
    {
        wchar_t csClassName[32];
        HWND hCurrWnd = (HWND)wParam;
        DWORD retProcId = NULL;
        GetClassName(hCurrWnd, csClassName, sizeof(csClassName));
        if ((wcscmp(csClassName, L"paneClassDC") == 0)
          ||(wcscmp(csClassName, L"screenClass") == 0))
        {
            int id = -1;
            DWORD windowThread = GetWindowThreadProcessId(hCurrWnd, NULL);
            for (int i=0; i < MAX_PPTS; i++)
            {
                if (pptView[i].dwThreadId == windowThread)
                {
                    id = i;
                    break;
                }
            }
            if (id >= 0)
            {
                if (wcscmp(csClassName, L"paneClassDC") == 0)
                {
                    pptView[id].hWnd2 = hCurrWnd;
                }
                else
                {
                    pptView[id].hWnd = hCurrWnd;
                    CBT_CREATEWND* cw = (CBT_CREATEWND*)lParam;
                    if (pptView[id].hParentWnd != NULL)
                    {
                        cw->lpcs->hwndParent = pptView[id].hParentWnd;
                    }
                    cw->lpcs->cy = pptView[id].rect.bottom
                        - pptView[id].rect.top;
                    cw->lpcs->cx = pptView[id].rect.right
                        - pptView[id].rect.left;
                    cw->lpcs->y = -32000;
                    cw->lpcs->x = -32000;
                }
                if ((pptView[id].hWnd != NULL) && (pptView[id].hWnd2 != NULL))
                {
                    UnhookWindowsHookEx(globalHook);
                    globalHook = NULL;
                    pptView[id].hook = SetWindowsHookEx(WH_CALLWNDPROC,
                        CwpProc, hInstance, pptView[id].dwThreadId);
                    pptView[id].msgHook = SetWindowsHookEx(WH_GETMESSAGE,
                        GetMsgProc, hInstance, pptView[id].dwThreadId);
                    Sleep(10);
                    pptView[id].state = PPT_OPENED;
                }
            }
        }
    }
    return CallNextHookEx(hook, nCode, wParam, lParam);
}

// This hook exists whilst the slideshow is loading but only listens on the
// slideshows thread. It listens out for mousewheel events
LRESULT CALLBACK GetMsgProc(int nCode, WPARAM wParam, LPARAM lParam)
{
    HHOOK hook = NULL;
    MSG *pMSG = (MSG *)lParam;
    DWORD windowThread = GetWindowThreadProcessId(pMSG->hwnd, NULL);
    int id = -1;
    for (int i = 0; i < MAX_PPTS; i++)
    {
        if (pptView[i].dwThreadId == windowThread)
        {
            id = i;
            hook = pptView[id].msgHook;
            break;
        }
    }
    if (id >= 0 && nCode == HC_ACTION && wParam == PM_REMOVE
        && pMSG->message == WM_MOUSEWHEEL)
    {
        if (pptView[id].state != PPT_LOADED)
        {
            if (pptView[id].currentSlide == 1)
            {
                pptView[id].firstSlideSteps++;
            }
            pptView[id].steps++;
            pptView[id].lastSlideSteps++;
        }
    }
    return CallNextHookEx(hook, nCode, wParam, lParam);
}
// This hook exists whilst the slideshow is running but only listens on the
// slideshows thread. It listens out for slide changes, message WM_USER+22.
LRESULT CALLBACK CwpProc(int nCode, WPARAM wParam, LPARAM lParam){
    CWPSTRUCT *cwp;
    cwp = (CWPSTRUCT *)lParam;
    HHOOK hook = NULL;
    wchar_t filename[MAX_PATH];

    DWORD windowThread = GetWindowThreadProcessId(cwp->hwnd, NULL);
    int id = -1;
    for (int i = 0; i < MAX_PPTS; i++)
    {
        if (pptView[i].dwThreadId == windowThread)
        {
            id = i;
            hook = pptView[id].hook;
            break;
        }
    }
    if ((id >= 0) && (nCode == HC_ACTION))
    {
        if (cwp->message == WM_USER + 22)
        {
            if (pptView[id].state != PPT_LOADED)
            {
                if ((pptView[id].currentSlide > 0)
                    && (pptView[id].previewPath != NULL
                    && wcslen(pptView[id].previewPath) > 0))
                {
                    swprintf_s(filename, MAX_PATH, L"%s%i.bmp",
                        pptView[id].previewPath,
                        pptView[id].currentSlide);
                    CaptureAndSaveWindow(cwp->hwnd, filename);
                }
                if (((cwp->wParam == 0)
                    || (pptView[id].slideNos[1] == cwp->wParam))
                    && (pptView[id].currentSlide > 0))
                {
                    pptView[id].state = PPT_LOADED;
                    pptView[id].currentSlide = pptView[id].slideCount + 1;
                }
                else
                {
                    if (cwp->wParam > 0)
                    {
                        pptView[id].currentSlide = pptView[id].currentSlide + 1;
                        pptView[id].slideNos[pptView[id].currentSlide]
                            = cwp->wParam;
                        pptView[id].slideCount = pptView[id].currentSlide;
                        pptView[id].lastSlideSteps = 0;
                    }
                }
            }
            else
            {
                if (cwp->wParam > 0)
                {
                    if(pptView[id].guess > 0
                        && pptView[id].slideNos[pptView[id].guess] == 0)
                    {
                        pptView[id].currentSlide = 0;
                    }
                    for(int i = 1; i <= pptView[id].slideCount; i++)
                    {
                        if(pptView[id].slideNos[i] == cwp->wParam)
                        {
                            pptView[id].currentSlide = i;
                            break;
                        }
                    }
                    if(pptView[id].currentSlide == 0)
                    {
                        pptView[id].slideNos[pptView[id].guess] = cwp->wParam;
                        pptView[id].currentSlide = pptView[id].guess;
                    }
                    pptView[id].guess = 0;
                }
            }
        }
        if ((pptView[id].state != PPT_CLOSED)

            &&(cwp->message == WM_CLOSE || cwp->message == WM_QUIT))
        {
            pptView[id].state = PPT_CLOSING;
        }
    }
    return CallNextHookEx(hook, nCode, wParam, lParam);
}

VOID CaptureAndSaveWindow(HWND hWnd, wchar_t* filename)
{
    HBITMAP hBmp;
    if ((hBmp = CaptureWindow(hWnd)) == NULL)
    {
        return;
    }
    RECT client;
    GetClientRect(hWnd, &client);
    UINT uiBytesPerRow = 3 * client.right; // RGB takes 24 bits
    UINT uiRemainderForPadding;

    if ((uiRemainderForPadding = uiBytesPerRow % sizeof(DWORD)) > 0)
        uiBytesPerRow += (sizeof(DWORD) - uiRemainderForPadding);

    UINT uiBytesPerAllRows = uiBytesPerRow * client.bottom;
    PBYTE pDataBits;

    if ((pDataBits = new BYTE[uiBytesPerAllRows]) != NULL)
    {
        BITMAPINFOHEADER bmi = {0};
        BITMAPFILEHEADER bmf = {0};

        // Prepare to get the data out of HBITMAP:
        bmi.biSize = sizeof(bmi);
        bmi.biPlanes = 1;
        bmi.biBitCount = 24;
        bmi.biHeight = client.bottom;
        bmi.biWidth = client.right;

        // Get it:
        HDC hDC = GetDC(hWnd);
        GetDIBits(hDC, hBmp, 0, client.bottom, pDataBits, (BITMAPINFO*) &bmi,
            DIB_RGB_COLORS);
        ReleaseDC(hWnd, hDC);

        // Fill the file header:
        bmf.bfOffBits = sizeof(bmf) + sizeof(bmi);
        bmf.bfSize = bmf.bfOffBits + uiBytesPerAllRows;
        bmf.bfType = 0x4D42;

        // Writing:
        FILE* pFile;
        int err = _wfopen_s(&pFile, filename, L"wb");
        if (err == 0)
        {
            fwrite(&bmf, sizeof(bmf), 1, pFile);
            fwrite(&bmi, sizeof(bmi), 1, pFile);
            fwrite(pDataBits, sizeof(BYTE), uiBytesPerAllRows, pFile);
            fclose(pFile);
        }
        delete [] pDataBits;
    }
    DeleteObject(hBmp);
}
HBITMAP CaptureWindow(HWND hWnd)
{
    HDC hDC;
    BOOL bOk = FALSE;
    HBITMAP hImage = NULL;

    hDC = GetDC(hWnd);
    RECT rcClient;
    GetClientRect(hWnd, &rcClient);
    if ((hImage = CreateCompatibleBitmap(hDC, rcClient.right, rcClient.bottom))
        != NULL)
    {
        HDC hMemDC;
        HBITMAP hDCBmp;

        if ((hMemDC = CreateCompatibleDC(hDC)) != NULL)
        {
            hDCBmp = (HBITMAP)SelectObject(hMemDC, hImage);
			HMODULE hLib = LoadLibrary(L"User32");
            // PrintWindow works for windows outside displayable area
            // but was only introduced in WinXP. BitBlt requires the window to
            // be topmost and within the viewable area of the display
            if (GetProcAddress(hLib, "PrintWindow") == NULL)
            {
                SetWindowPos(hWnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOSIZE);
                BitBlt(hMemDC, 0, 0, rcClient.right, rcClient.bottom, hDC, 0,
                    0, SRCCOPY);
                SetWindowPos(hWnd, HWND_NOTOPMOST, -32000, -32000, 0, 0,
                    SWP_NOSIZE);
            }
            else
            {
                PrintWindow(hWnd, hMemDC, 0);
            }
            SelectObject(hMemDC, hDCBmp);
            DeleteDC(hMemDC);
            bOk = TRUE;
        }
    }
    ReleaseDC(hWnd, hDC);
    if (!bOk)
    {
        if (hImage)
        {
            DeleteObject(hImage);
            hImage = NULL;
        }
    }
    return hImage;
}
