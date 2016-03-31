
import pprint
import subprocess
import os.path
import binascii
import sys
import telnetlib
import time
import re
import colorama
from colorama import *



global routerlist #[R1, R2, ...]
global visited_ip  
global entire_ip    #[[R1,192.168.2.1],[],[],...]
global ip_neighbor
global telnet_fail_ip
global username
global password

global TELNET_PORT 
global TELNET_TIMEOUT 
global READ_TIMEOUT 

username="teopy"
password="python"
routerlist=[]
visited_ip=[]
entire_ip=[]
ip_neighbor=[]
telnet_fail_ip=[]



def open_telnet_conn(ip):
    #Change exception message
    try:
        #Define telnet parameters
        
        userfile=open("userfile.txt","r")
        p=userfile.readlines()
        username=p[0].split(',')[0]
        password=p[0].split(',')[1].rstrip('\n')
        
        userfile.close()
        print "username: ", username
        print "password: ", password
        
        
        TELNET_PORT = 23
        TELNET_TIMEOUT = 5
        READ_TIMEOUT = 5
        
        #Logging into device
        connection = telnetlib.Telnet(ip, TELNET_PORT, TELNET_TIMEOUT)
        
        output = connection.read_until("name:", READ_TIMEOUT)
        connection.write(username + "\n")
        
        output = connection.read_until("word:", READ_TIMEOUT)
        connection.write(password + "\n")
        time.sleep(0.5)	
        
        print "Logging onto %s" %ip
        
        
        #Setting terminal length for entire output - no pagination
        connection.write("\n")
        time.sleep(0.5)
        output = connection.read_until("\n:", READ_TIMEOUT)
        routername=output.splitlines(1)[2][:-1]
        
        if routername not in routerlist:
            routerlist.append(routername)
            
                    
            connection.write("show ip interface brief" + '\n')
            time.sleep(0.5)
            output1 = connection.read_very_eager()
            regular_expression(output1,routername)
            #print output1
            #return output1
            
            connection.write("show ip route"+'\n')
            time.sleep(0.5)
            output2=connection.read_very_eager()
            regular_expression2(output2,routername)
    
            print "routerlist : ", routerlist
            print "visited_ip : ", visited_ip
            print "failed telnet : ", telnet_fail_ip

     
            for ip in ip_neighbor:
                
                ciscotelnet(ip, connection)
                             
            
            #Closing the connection
            connection.close()
        
        else:
            connection.close()
            return
        
    except IOError:
        print "Telnet Failed! Please check IP, username, or password."
        telnet_fail_ip.append(ip)

             

   

def ciscotelnet(ip,connection):
    print "\n NEXT IP 1 = ", ip
    
    connection.write("telnet " + ip + "\n")
    
    output = connection.read_until("name:",5)
    connection.write(username + "\n")
    output = connection.read_until("word:", 5)
    connection.write(password + "\n")
    time.sleep(0.5)	
 #   print "outputtest 2 : ", output
    print "Logging onto %s" %ip
    

    connection.write("\n")
    time.sleep(0.5)
    output = connection.read_until("\n:", 5)
    routername=output.splitlines(1)[2][:-1]
    
    
    if routername not in routerlist:
        routerlist.append(routername)
     
        connection.write("show ip interface brief" + '\n')
        time.sleep(0.5)
        output1 = connection.read_very_eager()
        regular_expression(output1,routername)
        #print output1
        #return output1
        
        connection.write("show ip route"+'\n')
        time.sleep(0.5)
        output2=connection.read_very_eager()
        regular_expression2(output2,routername)
        print "routerlist : ", routerlist
        print "visited_ip : ", visited_ip
        print "failed telnet : ", telnet_fail_ip

        for ip3 in ip_neighbor:
            if ip3 not in visited_ip:
                #print "\n NEXT IP 2 = ", ip3 
                #print "$$$$$$$$$$$$$$$$$$$$RECURSIVE CALL$$$$$$$$$$$$$$$$$$$$$$$$"
                ciscotelnet(ip3,connection)
            
            #print "\n NEXT IP 3= ", ip3
            #print "!!!!!!!!!!!!!!!!!11ip3 is  in visited-IPip!!!!!!!!!!!!!!!!!"
#            else:
#                connection.write("exit" + '\n')   


            




def regular_expression(input_str,router):
    try:
        
        input_list=input_str.splitlines(0)
        
        ######Slicing list to remove unnecessary lines
        #Slice top 2 lines
        input_list=input_list[2:]
    
        #slice bottom 1 line
        input_list=input_list[:-1]
        
        count=0
        upup_interface=[]
        
        
        for eachline in input_list:
            a=re.search(r"(.+?)\s{2,}(.+?)\s{2,}(.+?)\s{2,}(.+?)\s{2,}(.+?)\s{2,}", eachline)
            if a.group(4) == "up" and a.group(5)=="up":
                count+=1
                upup_interface.append(a.group(2))
        
        
        for interface in upup_interface:
            visited_ip.append(interface)
            
            entire_ip.append([router,interface])
        
        
       
            
    except IOError:
        sys.exit



def regular_expression2(input_str,router):
    try:
        
        input_list=input_str.splitlines(0)
        
        ######Slicing list to remove unnecessary lines
        #Slice top 11 lines
        input_list=input_list[11:]
    
        #slice bottom 1 line
        input_list=input_list[:-1]
        
        count=0
        #print "input list : ",input_list
        
        for eachline in input_list:
            if "via" in eachline:
                b=re.search(r"([v][i][a])\s(.+?)[,]\s", eachline)
                if b.group(2) not in ip_neighbor:
                    ip_neighbor.append(b.group(2))

        print "ipneighbor : ", ip_neighbor
        
        
        
       
            
    except IOError:
        sys.exit
    
 



firstip="192.168.2.101"            
#firstip="10.0.50.5"            
open_telnet_conn(firstip)


print "Router List : ",routerlist
print "Visited_Ip : ", visited_ip
print "Telnet Fail IP : ", telnet_fail_ip
print "\nIP for each Router Interface : "
for IP in entire_ip:
    print IP

    
    
    
