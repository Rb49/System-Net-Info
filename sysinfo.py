import subprocess
import re
 
def run_command(cmd):
    '''
    function to execute a command using windows cmd
    gets: str, a command to execute
    returns: command output
    '''
    return subprocess.Popen(cmd,
    shell = True,
    stdout = subprocess.PIPE,
    stderr = subprocess.PIPE,
    stdin = subprocess.PIPE).communicate()

def nic_name_ip(systeminfo):
    '''
    gets info recieved by 'systeminfo'
    return list of names, list of ip s

    'systeminfo' displays only 'real' nics unlike 'ipconfig /all'
    '''
    #get all nics names and ip from systeminfo
    names = []
    ip = []
    #split the string into lines
    systeminfo = re.split('\\n', systeminfo)
    start2count = False

    temp_ip = ['']
    counter = 0
    count_list = []
    for l in range(len(systeminfo)):
        i = systeminfo[l]
        #only scan when network cards are previewed
        if not start2count and i.rfind('Network Card(s):') != -1:
            start2count = True
        elif start2count:
            #every ip a nic has
            if re.search(r'[\[][0-9]{2}[\]]', i):
                if len(re.split('\[', i)[0]) != 27: #if string is ip
                    if ip[-1] == ['']: #remove extra [] added in names.append()
                        del ip[-1]
                    counter += 1
                    del count_list[-1] #cover last round counter
                    ip.append(i.split()[-1]) #line index of ip start
                    count_list.append(counter)
                else: #if string is nic name
                    names.append(' '.join(i.split()[1:])) #line index of name start
                    ip.append([''])
                    counter = 0
                    count_list.append(counter)

    #change ip string format
    ip_counter = 0
    temp_ip = []
    for i in range(len(count_list)):
        string = '\n'
        looped = False
        for c in range(count_list[i]):
            string += ip[ip_counter] + ', '
            looped = True
            ip_counter += 1
        if not looped:
            ip_counter += 1
            string += 'None  '
        string = string[1:(len(string) - 2)]
        temp_ip.append(string)

    return names, temp_ip

def nic_mac_dhcp_status(names, ipconfig):
    '''
    gets info recieved by 'ipconfig /all'
    return list of mac s, list of dhcp statuses, list of media connectivity statuses
    '''

    ipconfig = re.split('\\n', ipconfig) #split 'ipconfig' info

    mac_pattern = r'.*?[^:-]([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2}[^:-]).*?' #mac regex

    mac = ['' for x in range(len(names))] #an empty list by the size of 'names' for mac s
    dhcp = ['' for x in range(len(names))] #dhcp status list
    status = ['Connected' for x in range(len(names))] #media status list

    for i in range(len(ipconfig)):
        line = ipconfig[i]
        index = None
        for n in range(len(names)): #find the nic name to match a mac to it
            if line.rfind(names[n]) != -1:
                index = n
                break
        if index != None:
            #get mac data
            line = ipconfig[i + 1]
            match = re.search(mac_pattern, line).group(0)
            match = match.split()[-1] 
            mac[index] = match

            #get dhcp data
            line = ipconfig[i + 2]
            if line.rfind('DHCP Enabled') != -1: #just to make sure it's the right line. if somehow (won't happen) the format changes value will be empty.
                if line.rfind('Yes') != -1:
                    dhcp[index] = 'Yes'
                else:
                    dhcp[index] = 'No'  

            #get media status data
            line = ipconfig[i - 2]
            if line.rfind('Media State') != -1: 
                if line.rfind('disconnected') != -1:
                    status[index] = 'Disconnected'
 
    return mac, dhcp, status
            
def print_nic_info():
    '''
    function to print NIC info and format it
    gets: None
    returns: None
    '''
    #run subprocesses
    ipconfig = str(run_command('ipconfig /all')[0], encoding = 'utf-8', errors = 'ignore')
    systeminfo = str(run_command('systeminfo')[0], encoding = 'utf-8', errors = 'ignore')

    #get nics and their ip
    names, ip = nic_name_ip(systeminfo)
    #get nics mac, dhcp, status
    mac, dhcp, status = nic_mac_dhcp_status(names, ipconfig)

    #print 
    nic_info = []
    for i in range(len(names)):
        nic_info.append([names[i], status[i], mac[i], dhcp[i] , ip[i]])

    print('Your system\'s NIC information')
    print('------------------------------')
    print ('{:<50} {:<20} {:<20} {:<20} {:<50}'.format('NIC name', 'Media State', 'MAC address', 'DHCP enabled', 'IP addersses'))
    print ('{:<50} {:<20} {:<20} {:<20} {:<50}'.format('--------', '-----------', '-----------', '------------', '------------'))

    for v in nic_info:
        name, status, mac, ip, dhcp = v
        print ('{:<50} {:<20} {:<20} {:<20} {:<50}'.format( name, status, mac, ip, dhcp))

    return

def system_gateaway_ip(ipconfig):
    '''
     gets info recieved by 'ipconfig /all'
     returns str of gateaway ip, str of system ip
    '''
    ipconfig = re.split('\\n', ipconfig)

    #lists for ip and gateaway
    system_ip = ['None','None']
    gateaway = ['None','None']
    for lines in range(len(ipconfig)): #search for ip and gateaway
        i = ipconfig[lines]
        if i.rfind('Default Gateway') != -1:
            if i.split()[-1] not in gateaway and len(i.split()[-1]) >= 7: #ip minimal length is 7
                gateaway[0] = i.split()[-1]
            
            #try to add ipv4/ipv6
            i = ipconfig[lines + 1]
            if len(i.split()) == 1:
                if i.split()[-1] not in gateaway and len(i.split()[-1].split()[-1]) >= 7:
                    gateaway[1] = i.split()[0] 

            i = ipconfig[lines - 4]            
            if i.rfind('IPv4 Address') != -1:
                i = i.replace('(', ' ') #to make it not to present the 'prefered' address
                if i.split()[-1] not in system_ip:
                    system_ip[0] = i.split()[-2]

            i = ipconfig[lines - 7]
            if i.rfind('IPv6 Address') != -1 and i.rfind('Temporary') == -1 and i.rfind('Link') == -1:
                i = i.replace('(', ' ')
                if i.split()[-1] not in system_ip:
                    system_ip[1] = i.split()[-2]

    return str(gateaway[0] + ', ' + gateaway[1]), str(system_ip[0] + ', ' + system_ip[1])
    
def system_details(systeminfo):
    '''
    gets info recieved by 'systeminfo'
    returns tuple of system properties
    '''
    systeminfo = re.split('\\n', systeminfo)

    #bunch of system properties
    hostname = ' '.join(systeminfo[1].split()[2:])
    osName = ' '.join(systeminfo[2].split()[2:])
    regOwner = ' '.join(systeminfo[7].split()[2:])
    time = ' '.join(systeminfo[23].split()[2:])

    return hostname, osName, regOwner, time

def print_system_info():
    '''
    function to print system info and format it
    gets: None
    returns: None
    '''
    #run subprocesses
    ipconfig = str(run_command('ipconfig /all')[0], encoding = 'utf-8', errors = 'ignore')
    systeminfo = str(run_command('systeminfo')[0], encoding = 'utf-8', errors = 'ignore')

    gateaway, system_ip = system_gateaway_ip(ipconfig)

    hostname, osName, regOwner, time = system_details(systeminfo)

    #print
    print(f'''Your system\'s general information
              \r----------------------------------
              \rHost name:  {hostname}
              \rOS name:  {osName}
              \rRegistered owner:  {regOwner}
              \rTime zone:  {time}
              \rIP adresses:  {system_ip}
              \rGateaway addresses:  {gateaway}
             ''')

    return

def main():
    '''
    main function
    gets and return None
    '''
    print('Welcome to system information program!\nPlease use full screen\n\n')
    print_nic_info()
    print('\n\n')
    print_system_info()
    print('\n')

    return

if __name__ == '__main__':
    #try except block
    try:
        main()
    except:
        print('Unknown error occured.\nPlease try again.')
    finally:
        input('Enter to quit...')
        quit()