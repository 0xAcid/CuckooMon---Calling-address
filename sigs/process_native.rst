Signature::

    * Calling convention: WINAPI
    * Category: process
    * Library: ntdll
    * Return value: NTSTATUS


NtCreateProcess
===============

Parameters::

    ** PHANDLE ProcessHandle process_handle
    ** ACCESS_MASK DesiredAccess desired_access
    *  POBJECT_ATTRIBUTES ObjectAttributes
    *  HANDLE ParentProcess
    ** BOOLEAN InheritObjectTable inherit_handles
    *  HANDLE SectionHandle
    *  HANDLE DebugPort
    *  HANDLE ExceptionPort

Flags::

    desired_access

Pre::

    wchar_t *filepath = get_unicode_buffer();
    path_get_full_path_objattr(ObjectAttributes, filepath);

    wchar_t *filepath_r = NULL;
    if(ObjectAttributes != NULL && ObjectAttributes->ObjectName != NULL) {
        filepath_r = ObjectAttributes->ObjectName->Buffer;
    }

Interesting::

    u filepath
    i desired_access
    i inherit_handles

Middle::

    uint32_t pid = pid_from_process_handle(*ProcessHandle);

Logging::

    i process_identifier pid
    u filepath filepath
    u filepath_r filepath_r

Post::

    if(NT_SUCCESS(ret) != FALSE) {
        pipe("PROCESS:%d", pid);
        sleep_skip_disable();
    }

    free_unicode_buffer(filepath);


NtCreateProcessEx
=================

Parameters::

    ** PHANDLE ProcessHandle process_handle
    ** ACCESS_MASK DesiredAccess desired_access
    *  POBJECT_ATTRIBUTES ObjectAttributes
    *  HANDLE ParentProcess
    ** ULONG Flags flags
    *  HANDLE SectionHandle
    *  HANDLE DebugPort
    *  HANDLE ExceptionPort
    *  BOOLEAN InJob

Flags::

    desired_access

Pre::

    wchar_t *filepath = get_unicode_buffer();
    path_get_full_path_objattr(ObjectAttributes, filepath);

    wchar_t *filepath_r = NULL;
    if(ObjectAttributes != NULL && ObjectAttributes->ObjectName != NULL) {
        filepath_r = ObjectAttributes->ObjectName->Buffer;
    }

Interesting::

    u filepath
    i desired_access
    i flags

Middle::

    uint32_t pid = pid_from_process_handle(*ProcessHandle);

Logging::

    i process_identifier pid
    u filepath filepath
    u filepath_r filepath_r

Post::

    if(NT_SUCCESS(ret) != FALSE) {
        pipe("PROCESS:%d", pid);
        sleep_skip_disable();
    }

    free_unicode_buffer(filepath);


NtCreateUserProcess
===================

Signature::

    * Prune: resolve

Parameters::

    ** PHANDLE ProcessHandle process_handle
    ** PHANDLE ThreadHandle thread_handle
    ** ACCESS_MASK ProcessDesiredAccess desired_access_process
    ** ACCESS_MASK ThreadDesiredAccess desired_access_thread
    *  POBJECT_ATTRIBUTES ProcessObjectAttributes
    *  POBJECT_ATTRIBUTES ThreadObjectAttributes
    ** ULONG ProcessFlags flags_process
    ** ULONG ThreadFlags flags_thread
    *  PRTL_USER_PROCESS_PARAMETERS ProcessParameters
    *  PPS_CREATE_INFO CreateInfo
    *  PPS_ATTRIBUTE_LIST AttributeList

Flags::

    desired_access_process
    desired_access_thread

Pre::

    wchar_t *process_name = get_unicode_buffer();
    path_get_full_path_objattr(ProcessObjectAttributes, process_name);

    wchar_t *process_name_r = NULL;
    if(ProcessObjectAttributes != NULL &&
            ProcessObjectAttributes->ObjectName != NULL) {
        process_name_r = ProcessObjectAttributes->ObjectName->Buffer;
    }

    wchar_t *thread_name = get_unicode_buffer();
    path_get_full_path_objattr(ThreadObjectAttributes, thread_name);

    wchar_t *thread_name_r = NULL;
    if(ThreadObjectAttributes != NULL &&
            ThreadObjectAttributes->ObjectName != NULL) {
        thread_name_r = ThreadObjectAttributes->ObjectName->Buffer;
    }

    wchar_t *filepath =
        extract_unicode_string(&ProcessParameters->ImagePathName);
    wchar_t *command_line =
        extract_unicode_string(&ProcessParameters->CommandLine);

Middle::

    uint32_t pid = pid_from_process_handle(*ProcessHandle);
    uint32_t tid = tid_from_thread_handle(*ThreadHandle);

Logging::

    i process_identifier pid
    i thread_identifier tid
    u process_name process_name
    u process_name_r process_name_r
    u thread_name thread_name
    u thread_name_r thread_name_r
    u filepath filepath
    u command_line command_line

Post::

    if(NT_SUCCESS(ret) != FALSE) {
        pipe("PROCESS2:%d,%d,%d", pid, tid, HOOK_MODE_ALL);
        sleep_skip_disable();
    }

    free_unicode_buffer(process_name);
    free_unicode_buffer(thread_name);
    free_unicode_buffer(filepath);
    free_unicode_buffer(command_line);


RtlCreateUserProcess
====================

Parameters::

    *  PUNICODE_STRING ImagePath
    ** ULONG ObjectAttributes flags
    *  PRTL_USER_PROCESS_PARAMETERS ProcessParameters
    *  PSECURITY_DESCRIPTOR ProcessSecurityDescriptor
    *  PSECURITY_DESCRIPTOR ThreadSecurityDescriptor
    *  HANDLE ParentProcess
    ** BOOLEAN InheritHandles inherit_handles
    *  HANDLE DebugPort
    *  HANDLE ExceptionPort
    *  PRTL_USER_PROCESS_INFORMATION ProcessInformation

Pre::

    wchar_t *filepath = get_unicode_buffer();
    path_get_full_path_unistr(ImagePath, filepath);

    wchar_t *filepath_r = NULL;
    if(ImagePath != NULL) {
        filepath_r = ImagePath->Buffer;
    }

Interesting::

    u filepath
    i flags
    i inherit_handles

Middle::

    uint32_t pid = pid_from_process_handle(ProcessInformation->ProcessHandle);
    uint32_t tid = tid_from_thread_handle(ProcessInformation->ThreadHandle);

Logging::

    i process_identifier pid
    i thread_identifier tid
    u filepath filepath
    u filepath_r filepath_r

Post::

    if(NT_SUCCESS(ret) != FALSE) {
        pipe("PROCESS2:%d,%d,%d", pid, tid, HOOK_MODE_ALL);
        sleep_skip_disable();
    }

    free_unicode_buffer(filepath);


NtOpenProcess
=============

Parameters::

    ** PHANDLE ProcessHandle process_handle
    ** ACCESS_MASK DesiredAccess desired_access
    *  POBJECT_ATTRIBUTES ObjectAttributes
    *  PCLIENT_ID ClientId

Flags::

    desired_access

Ensure::

    ClientId

Logging::

    i process_identifier (uint32_t) (uintptr_t) ClientId->UniqueProcess


NtTerminateProcess
==================

Signature::

    * Prelog: instant

Parameters::

    ** HANDLE ProcessHandle process_handle
    ** NTSTATUS ExitStatus status_code

Pre::

    uint32_t pid = pid_from_process_handle(ProcessHandle);

    // If the process handle is a nullptr then it will kill all threads in
    // the current process except for the current one. TODO Should we have
    // any special handling for that? Perhaps the unhook detection logic?
    if(ProcessHandle != NULL) {
        pipe("KILL:%d", pid);
    }

Logging::

    i process_identifier pid


NtCreateSection
===============

Parameters::

    ** PHANDLE SectionHandle section_handle
    ** ACCESS_MASK DesiredAccess desired_access
    *  POBJECT_ATTRIBUTES ObjectAttributes
    *  PLARGE_INTEGER MaximumSize
    ** ULONG SectionPageProtection protection
    *  ULONG AllocationAttributes
    ** HANDLE FileHandle file_handle

Flags::

    desired_access

Pre::

    wchar_t *section_name = NULL;
    if(ObjectAttributes != NULL) {
        section_name = extract_unicode_string(ObjectAttributes->ObjectName);
    }

    HANDLE object_handle = NULL;
    if(ObjectAttributes != NULL) {
        object_handle = ObjectAttributes->RootDirectory;
    }

Logging::

    l object_handle (uintptr_t) object_handle
    u section_name section_name

Post::

    if(section_name != NULL) {
        free_unicode_buffer(section_name);
    }


NtMakeTemporaryObject
=====================

Parameters::

    ** HANDLE ObjectHandle handle


NtMakePermanentObject
=====================

Parameters::

    ** HANDLE ObjectHandle handle


NtOpenSection
=============

Parameters::

    ** PHANDLE SectionHandle section_handle
    ** ACCESS_MASK DesiredAccess desired_access
    *  POBJECT_ATTRIBUTES ObjectAttributes

Flags::

    desired_access

Pre::

    wchar_t *section_name = NULL;
    if(ObjectAttributes != NULL) {
        section_name = extract_unicode_string(ObjectAttributes->ObjectName);
    }

Logging::

    u section_name section_name

Post::

    if(section_name != NULL) {
        free_unicode_buffer(section_name);
    }


NtUnmapViewOfSection
====================

Parameters::

    ** HANDLE ProcessHandle process_handle
    ** PVOID BaseAddress base_address

Pre::

    MEMORY_BASIC_INFORMATION_CROSS mbi; uintptr_t region_size = 0;
    if(virtual_query_ex(ProcessHandle, BaseAddress, &mbi) != FALSE) {
        region_size = mbi.RegionSize;
    }

Logging::

    i process_identifier pid_from_process_handle(ProcessHandle)
    l region_size region_size


NtAllocateVirtualMemory
=======================

Parameters::

    ** HANDLE ProcessHandle process_handle
    ** PVOID *BaseAddress base_address
    *  ULONG_PTR ZeroBits
    ** PSIZE_T RegionSize region_size
    ** ULONG AllocationType allocation_type
    ** ULONG Protect protection

Flags::

    protection
    allocation_type

Logging::

    i process_identifier pid_from_process_handle(ProcessHandle)


NtReadVirtualMemory
===================

Parameters::

    ** HANDLE ProcessHandle process_handle
    ** LPCVOID BaseAddress base_address
    *  LPVOID Buffer
    *  SIZE_T NumberOfBytesToRead
    *  PSIZE_T NumberOfBytesReaded

Ensure::

    NumberOfBytesReaded

Logging::

    B buffer NumberOfBytesReaded, Buffer


NtWriteVirtualMemory
====================

Parameters::

    ** HANDLE ProcessHandle process_handle
    ** LPVOID BaseAddress base_address
    *  LPCVOID Buffer
    *  SIZE_T NumberOfBytesToWrite
    *  PSIZE_T NumberOfBytesWritten

Ensure::

    NumberOfBytesWritten

Logging::

    i process_identifier pid_from_process_handle(ProcessHandle)
    !B buffer NumberOfBytesWritten, Buffer


NtProtectVirtualMemory
======================

Parameters::

    ** HANDLE ProcessHandle process_handle
    ** PVOID *BaseAddress base_address
    ** PSIZE_T NumberOfBytesToProtect length
    ** ULONG NewAccessProtection protection
    *  PULONG OldAccessProtection

Flags::

    protection

Logging::

    i process_identifier pid_from_process_handle(ProcessHandle)


NtFreeVirtualMemory
===================

Parameters::

    ** HANDLE ProcessHandle process_handle
    ** PVOID *BaseAddress base_address
    ** PSIZE_T RegionSize size
    ** ULONG FreeType free_type

Logging::

    i process_identifier pid_from_process_handle(ProcessHandle)


NtMapViewOfSection
==================

Parameters::

    ** HANDLE SectionHandle section_handle
    ** HANDLE ProcessHandle process_handle
    ** PVOID *BaseAddress base_address
    *  ULONG_PTR ZeroBits
    ** SIZE_T CommitSize commit_size
    ** PLARGE_INTEGER SectionOffset section_offset
    ** PSIZE_T ViewSize view_size
    *  UINT InheritDisposition
    ** ULONG AllocationType allocation_type
    ** ULONG Win32Protect win32_protect

Flags::

    allocation_type
    win32_protect

Middle::

    uintptr_t buflen = 0; uint8_t *buffer = NULL;

    uint32_t pid = pid_from_process_handle(ProcessHandle);

    if(NT_SUCCESS(ret) != FALSE && pid != get_current_process_id()) {

        // The actual size of the mapped view.
        buflen = *ViewSize;

        // As it is non-trivial to extract the base address of the original
        // mapped section, we'll just go ahead and read the memory from the
        // remote process.
        buffer = mem_alloc(buflen);
        if(buffer != NULL) {
            virtual_read_ex(ProcessHandle, *BaseAddress, buffer, &buflen);
        }
    }

Logging::

    i process_identifier pid
    !b buffer buflen, buffer

Post::

    if(NT_SUCCESS(ret) != FALSE) {
        pipe("PROCESS:%d", pid);
        sleep_skip_disable();
    }

    mem_free(buffer);
