[app]
title = Сюрприз
package.name = surprise
package.domain = org.redsba

source.dir = .
source.include_exts = py,png,jpg,jpeg,mp4,html,css,js,ttf,json

version = 1.0

requirements = python3,kivy,pyjnius

orientation = portrait

android.permissions = INTERNET
android.accept_sdk_license = True

android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
