#ifndef RADROOTS_EXPORT_H
#define RADROOTS_EXPORT_H

#if defined(_WIN32)
#if defined(RADROOTS_STATIC)
#define RADROOTS_API __cdecl
#elif defined(RADROOTS_BUILDING_SHARED)
#define RADROOTS_API __declspec(dllexport) __cdecl
#else
#define RADROOTS_API __declspec(dllimport) __cdecl
#endif
#else
#define RADROOTS_API __attribute__((visibility("default")))
#endif

#endif
