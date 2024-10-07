import os
import sys
import json
import zipfile
import platform
import re

def get_minecraft_path():
    if sys.platform.startswith('linux'):
        return os.path.expanduser("~/.minecraft")
    elif sys.platform.startswith('win'):
        return os.path.join(os.getenv("APPDATA"), ".minecraft")
    elif sys.platform.startswith('darwin'):
        return os.path.expanduser("~/Library/Application Support/minecraft")
    else:
        print("Cannot detect version: %s. Please report to your closest sysadmin" % sys.platform)
        sys.exit()

def get_natives_keyword():
    if sys.platform.startswith('linux'):
        return "linux"
    elif sys.platform.startswith('win'):
        return "windows"
    elif sys.platform.startswith('darwin'):
        return "osx"
    else:
        print("Cannot detect version: %s. Please report to your closest sysadmin" % sys.platform)
        sys.exit()

def check_mc_dir(src, version):
    # Check if the version of Minecraft is available for analysis
    if not os.path.exists(src) \
            or not os.path.exists(os.path.join(src, "versions")) \
            or not os.path.exists(os.path.join(src, "libraries")) \
            or not os.path.exists(os.path.join(src, "versions", version)):
        print("ERROR: You should run the launcher at least once before starting MCP")
        sys.exit()

def get_json_filename(src, version):
    return os.path.join(src, "versions", version, "%s.json" % version)

def check_cache_integrity(root, json_file, os_keyword, version):
    libraries = get_libraries(root, json_file, os_keyword)

    if libraries is None:
        return False

    for library in libraries.values():
        if not check_library_exists(root, library):
            return False

    if not check_minecraft_exists(root, version):
        return False

    natives = get_natives(root, libraries)

    for native in natives.keys():
        if not check_native_exists(root, native, version):
            return False

    return True

def check_library_exists(dst, library):
    return os.path.exists(os.path.join(dst, library['filename']))

def check_minecraft_exists(root, version):
    return os.path.exists(os.path.join(root, "versions", version, '%s.jar' % version)) and \
           os.path.exists(os.path.join(root, "versions", version, '%s.json' % version))

def check_native_exists(root, native, version):
    native_path = get_native_path(root, version)
    return os.path.exists(os.path.join(native_path, native))

def get_natives(root, libraries):
    native_list = {}
    for library in libraries.values():
        if library['extract']:
            src_path = os.path.join(root, library['filename'])
            jar_file = zipfile.ZipFile(src_path)
            file_list = jar_file.namelist()

            for _file in file_list:
                exclude = False
                for entry in library['exclude']:
                    if entry in _file:
                        exclude = True
                if not exclude:
                    native_list[_file] = library['filename']
    return native_list

def get_native_path(root, version):
    return os.path.join(root, "versions", version, "%s-natives" % version)

def get_libraries(root, json_file, os_keyword):
    if not os.path.exists(json_file):
        return None
    
    try:
        with open(json_file, 'r') as file:
            json_data = json.load(file)
    except Exception as e:
        print("Error while parsing the library JSON file: %s" % e)
        sys.exit()

    mc_libraries = json_data['libraries']
    out_libraries = {}

    for library in mc_libraries:
        lib_canonical = library['name'].split(':')[0]
        lib_subdir = library['name'].split(':')[1]
        lib_version = library['name'].split(':')[2]
        lib_path = lib_canonical.replace('.', '/')
        extract = False
        exclude = []

        # Apply rules
        if 'rules' in library:
            pass_rules = False
            for rule in library['rules']:
                rule_applies = True
                if 'os' in rule:
                    if rule['os']['name'] != os_keyword:
                        rule_applies = False
                    else:
                        if os_keyword == "osx":
                            os_ver = platform.mac_ver()[0]
                        else:
                            os_ver = platform.release()

                        if not re.match(rule['os']['version'], os_ver):
                            rule_applies = False

                if rule_applies:
                    if rule['action'] == "allow":
                        pass_rules = True
                    else:
                        pass_rules = False

            if not pass_rules:
                continue

        if 'natives' in library:
            lib_filename = "%s-%s-%s.jar" % (lib_subdir, lib_version, library['natives'][os_keyword])
        else:
            lib_filename = "%s-%s.jar" % (lib_subdir, lib_version)

        if 'extract' in library:
            extract = True
            if 'exclude' in library['extract']:
                exclude.extend(library['extract']['exclude'])

        lib_relative_path = os.path.join("libraries", lib_path, lib_subdir, lib_version, lib_filename)

        out_libraries[lib_subdir] = {
            'name': library['name'],
            'filename': lib_relative_path,
            'extract': extract,
            'exclude': exclude
        }

    return out_libraries


if __name__ == '__main__':
    os_keyword = get_natives_keyword()
    mc_dir = get_minecraft_path()
    mc_libraries = get_libraries(mc_dir, get_json_filename(mc_dir, "1.6.1"), os_keyword)
    mc_natives = get_natives(mc_dir, mc_libraries)

    for native in mc_natives.keys():
        if check_native_exists("./jars", native, "1.6.1"):
            print('Found %s %s' % (native, mc_natives[native]))
        else:
            print('Not found %s %s' % (native, mc_natives[native]))
