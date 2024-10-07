'''
Created on Jun 30, 2013

@author: kickban
'''
import os
import sys
import shutil
import zipfile
from commands import Commands
import runtime.minecraftdiscovery as minecraftdiscovery


def copyAssets(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    try:
        shutil.copytree(src, dst)
    except:
        print("Error copying assets.")
        sys.exit()


def copyLibrary(src, dst, library):
    try:
        dstPath = os.path.split(os.path.join(dst, library['filename']))[0]
        if os.path.exists(dstPath):
            shutil.rmtree(dstPath)
        os.makedirs(dstPath)
        shutil.copy2(os.path.join(src, library['filename']), dstPath)
    except:
        print("Error copying library %s" % library['name'])
        sys.exit()


def extractNative(root, name, jarname, version):
    try:
        srcPath = os.path.join(root, jarname)
        dstPath = os.path.join(root, "versions", version,
                               "%s-natives" % version)

        if not os.path.exists(dstPath):
            os.makedirs(dstPath)

        jarFile = zipfile.ZipFile(srcPath)
        jarFile.extract(name, dstPath)
    except:
        print("Error extracting native %s from %s" % (name, jarname))
        sys.exit()


def copyMinecraft(src, dst, version):
    try:
        jarSrcPath = os.path.join(src, "versions", version, "%s.jar" % version)
        jsonSrcPath = os.path.join(
            src, "versions", version, "%s.json" % version)
        dstPath = os.path.join(dst, "versions", version)

        if os.path.exists(dstPath):
            shutil.rmtree(dstPath)
        os.makedirs(dstPath)

        shutil.copy2(jarSrcPath, dstPath)
        shutil.copy2(jsonSrcPath, dstPath)
    except Exception as e:
        print("\nError while copying Minecraft : %s" % e)
        sys.exit()


def copyClientAssets(commands, workDir=None):
    currentVersion = commands.versionClient

    osKeyword = minecraftdiscovery.get_natives_keyword()
    if workDir == None:
        if minecraftdiscovery.check_cache_integrity(commands.dirjars, commands.jsonFile, osKeyword, currentVersion):
            return
        else:
            mcDir = minecraftdiscovery.get_minecraft_path()
    else:
        mcDir = workDir

    dstDir = commands.dirjars
    print("Looking in %s for mc installs..." %
          os.path.join(mcDir, "versions")),
    minecraftdiscovery.check_mc_dir(mcDir, currentVersion)
    print("OK")

    print("Copying assets..."),
    copyAssets(os.path.join(mcDir, "assets"), os.path.join(dstDir, "assets"))
    print("OK")

    print("Parsing JSON file..."),
    mcLibraries = minecraftdiscovery.get_libraries(
        mcDir, minecraftdiscovery.getJSONFilename(mcDir, currentVersion), osKeyword)
    print("OK")

    print("Looking for minecraft main jar..."),
    if (minecraftdiscovery.check_minecraft_exists(dstDir, currentVersion)):
        print("OK")
    else:
        print("Not found")
        print("Copying minecraft main jar..."),
        copyMinecraft(mcDir, dstDir, currentVersion)
        print("OK")

    print("> Checking libraries...")
    for library in mcLibraries.values():
        if not minecraftdiscovery.check_library_exists(dstDir, library):
            print("\tCopying library %s..." % library['name'].split(':')[1]),
            copyLibrary(mcDir, dstDir, library)
            print("OK")

    print("> Checking Natives...")
    for native, jarname in minecraftdiscovery.get_natives(dstDir, mcLibraries).items():
        if not minecraftdiscovery.check_native_exists(dstDir, native, currentVersion):
            print("\tExtracting native %s..." % native),
            extractNative(dstDir, native, jarname, currentVersion)
            print("OK")


if __name__ == '__main__':
    commands = Commands()
    copyClientAssets(commands)
