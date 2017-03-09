$url = "http://172.16.9.71"
function Create-AesManagedObject($key, $IV) {
    $aesManaged = New-Object "System.Security.Cryptography.AesManaged"
    $aesManaged.Mode = [System.Security.Cryptography.CipherMode]::CBC
    $aesManaged.Padding = [System.Security.Cryptography.PaddingMode]::Zeros
    $aesManaged.BlockSize = 128
    $aesManaged.KeySize = 256
    if ($IV) {
        if ($IV.getType().Name -eq "String") {
            $aesManaged.IV = [System.Convert]::FromBase64String($IV)
        }
        else {
            $aesManaged.IV = $IV
        }
    }
    if ($key) {
        if ($key.getType().Name -eq "String") {
            $aesManaged.Key = [System.Convert]::FromBase64String($key)
        }
        else {
            $aesManaged.Key = $key
        }
    }
    $aesManaged
}

function Create-AesKey() {
    $aesManaged = Create-AesManagedObject
    $aesManaged.GenerateKey()
    [System.Convert]::ToBase64String($aesManaged.Key)
}

function Encrypt-String($key, $unencryptedString) {
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($unencryptedString)
    $aesManaged = Create-AesManagedObject $key
    $encryptor = $aesManaged.CreateEncryptor()
    $encryptedData = $encryptor.TransformFinalBlock($bytes, 0, $bytes.Length);
    [byte[]] $fullData = $aesManaged.IV + $encryptedData
    $aesManaged.Dispose()
    [System.Convert]::ToBase64String($fullData)
}

function Decrypt-String($key, $encryptedStringWithIV) {
    $bytes = [System.Convert]::FromBase64String($encryptedStringWithIV)
    $IV = $bytes[0..15]
    $aesManaged = Create-AesManagedObject $key $IV
    $decryptor = $aesManaged.CreateDecryptor();
    $unencryptedData = $decryptor.TransformFinalBlock($bytes, 16, $bytes.Length - 16);
    $aesManaged.Dispose()
    [System.Text.Encoding]::UTF8.GetString($unencryptedData).Trim([char]0)
}
$key = Create-AesKey
$userinfo = @{ Username = ([Environment]::UserName);
               Domainname = ([Environment]::UserDomainName);
               Computername = ([Environment]::MachineName)
              }
if ( $PSVersionTable.PSVersion.Major -lt 3) { 
  function ConvertTo-Json20([object] $item){
    add-type -assembly system.web.extensions
    $ps_js=new-object system.web.script.serialization.javascriptSerializer
    return $ps_js.Serialize($item)
  }
  $hash_error = @{ Version = ($PSVersionTable.PSVersion.Major);
                   Timeinfo = [System.DateTime]::Now;
                   Userinfo = $userinfo
  }
  $JSON_error = ConvertTo-Json20 $hash_error
  $webRequest = [System.Net.WebRequest]::Create($url)
  $UserAgent = "Watcher for sea"
  $webRequest.UserAgent = $("{0} (PowerShell {1}; .NET CLR {2}; {3})" -f $UserAgent, $(if($Host.Version){$Host.Version}else{"1.0"}),  
                           [Environment]::Version,  
                           [Environment]::OSVersion.ToString().Replace("Microsoft Windows ", "Win"))
  $encodedContent = [System.Text.Encoding]::UTF8.GetBytes($JSON_error)
  $webRequest.Method = "POST"
  $webRequest.KeepAlive = $true
  $webRequest.Pipelined = $true
  $webRequest.ContentType='application/json'
  $webRequest.Accept='application/json'
  if($encodedContent.length -gt 0) {
    $webRequest.ContentLength = $encodedContent.length
    $requestStream = $webRequest.GetRequestStream()
    $requestStream.Write($encodedContent, 0, $encodedContent.length)
    $requestStream.Close()
  }
  Exit
} 
else {
Function Get-LocalGroup  {
  [Cmdletbinding()] 
  Param( 
  [Parameter(ValueFromPipeline=$True, ValueFromPipelineByPropertyName=$True)] 
  [String[]]$Computername =  $Env:COMPUTERNAME,
  [parameter()]
  [string[]]$Group
  )
  Begin {
  Function  ConvertTo-SID {
  Param([byte[]]$BinarySID)
  (New-Object  System.Security.Principal.SecurityIdentifier($BinarySID,0)).Value
}
        Function  Get-LocalGroupMember {
  Param  ($Group)
  $group.Invoke('members')  | ForEach {
  $_.GetType().InvokeMember("Name",  'GetProperty',  $null,  $_, $null)
  }
  }
  }
  Process  {
  ForEach  ($Computer in  $Computername) {
  Try  {
  Write-Verbose  "Connecting to $($Computer)"
  $adsi  = [ADSI]"WinNT://$Computer"
  If  ($PSBoundParameters.ContainsKey('Group')) {
  Write-Verbose  "Scanning for groups: $($Group -join ',')"
  $Groups  = ForEach  ($item in  $group) {                        
  $adsi.Children.Find($Item, 'Group')
  }
  } Else  {
  Write-Verbose  "Scanning all groups"
  $groups  = $adsi.Children | where {$_.SchemaClassName -eq  'group'}
  }
  If  ($groups) {
  $groups  | ForEach {
  [pscustomobject]@{
  Computername = $Computer
  Name = $_.Name[0]
  Members = ((Get-LocalGroupMember  -Group $_))  -join ', '
  SID = (ConvertTo-SID -BinarySID $_.ObjectSID[0])
  }
  }
  } Else  {
  Throw  "No groups found!"
  }
  } Catch  {
  Write-Warning  "$($Computer): $_"
  }
  }
  }
  }
$prog = Get-WmiObject Win32_Product | select-object IdentifyingNumber, Name, Vendor, Version, Caption, InstallDate, InstallLocation, InstallState
$programs = @{ Name = $prog.Name;
               Vendor = $prog.Vendor;
               Version = $prog.Version;
               Caption = $prog.Caption;
               InstallDate = $prog.InstallDate;
               InstallLocation = $prog.InstallLocation;
               InstallState = $prog.InstallState
              }
$gpo = gpresult.exe /r
$event = Get-EventLog -List | ForEach-Object { $date = [DateTime]::Today.AddDays(-1).AddHours(1)
Try   { New-Object PSObject -Property @{ Name = $_.Log;
                                                  logs = (Get-EventLog -logname $_.Log -EntryType Error -After $date | Select-Object Time, EntryType, Sourse, InstanceID, Message)}                                            
} Catch { }
} 
$eventlog = @{ Name = $event.Name;
               Logs = $event.Logs
              }
$adapt = Get-NetAdapter | Select-Object name, interface, description, Status, MacAddress, Speed
$networkadapter = @{ Name = $adapt.Name;
                     Interface = $adapt.interface;
                     Description = $adapt.description;
                     Status = $adapt.Status;
                     MacAddress = $adapt.MacAddress;
                     Speed = $adapt.Speed
                    }
$srv = Get-WmiObject -Class Win32_Service | select-object Description, DisplayName, ExitCode, InstallDate, Name, ServiceType, StartMode, State, Status
$service = @{ Name = $srv.Name;
              DisplayName = $srv.DisplayName;
              Description = $srv.Description;
              ServiceType = $srv.ServiceType;
              ExitCode = $srv.ExitCode;
              InstallDate = $srv.InstallDate;
              StartMode = $srv.StartMode;
              State = $srv.State;
              Status = $srv.Status
             }
$groups = Get-LocalGroup -Computername  $env:COMPUTERNAME | Select-Object name, Members, SID
$net = Get-WmiObject Win32_NetworkAdapter | Select-Object name, AdapterType, MACAddress, DeviceID, LastErrorCode, Speed, Status, NetworkAddresses
$network = @{ Name = $net.name;
              AdapterType = $net.AdapterType;
              MACAddress = $net.MACAddress;
              DeviceID = $net.DeviceID;
              NetworkAddresses = $net.NetworkAddresses;
              Speed = $net.Speed;
              Status = $net.Status;
              ErrorCode = $net.LastErrorCode
             }
$vid = Get-WmiObject Win32_videoController | Select-Object name, AdapterRAM, VideoProcessor, CurrentHorizontalResolution, CurrentVerticalResolution, Status
$video = @{ Name = $vid.Name;
            AdapterRAM = $vid.AdapterRAM;
            VideoProcessor = $vid.VideoProcessor;
            CurrentHorizontalResolution = $vid.CurrentHorizontalResolution;
            CurrentVerticalResolution = $vid.CurrentVerticalResolution;
            Status = $vid.Status
           }
$mem = Get-WmiObject Win32_Physicalmemory | Select-Object capacity, DeviceLocator
$memory = @{ Capacity = $mem.capacity;
             DeviceLocator = $mem.DeviceLocator
            }
$lgdisk = Get-WmiObject Win32_LogicalDisk | select-object Name, ProviderName, MediaType, Access, DeviceID, Description, DriveType, FileSystem, Size, FreeSpace, InstallDate, Status, LastErrorCode, ErrorCleared, ErrorDescription 
$partions = @{ Disk = $lgdisk.DeviceID;
               Type = $lgdisk.DriverType;
               Size = $lgdisk.Size;
               FileSystem = $lgdisk.FileSystem;
               FreeSpace = $lgdisk.FreeSpace;
               InstallDate = $lgdisk.InstallDate;
               Status = $lgdisk.Status;
               ErrorCode = $lgdisk.LastErrorCode
              }
$phdisk = Get-WmiObject Win32_DiskDrive | select-object Model, Partitions, Size, interfacetype, InstallDate, LastErrorCode, Manufacturer, Status
$disks = @{ Model = $phdisk.Model;
            Partions = $phdisk.Partions;
            Size = $phdisk.Size;
            Type = $phdisk.interfacetype;
            InstallDate = $phdisk.InstallDate;
            Status = $phdisk.Status;
            Vendor = $phdisk.Manufacturer;
            ErrorCode = $phdisk.LastErrorCode
           }
$mom = Get-WmiObject Win32_BaseBoard | select-object Name, Model, SerialNumber, Product, Manufacturer
$motherboard = @{ Motherboard = $mom.Name;
                  Model = $mom.Model;
                  SerialNumber = $mom.SerialNumber;
                  Vendor = $mom.Manufacturer;
                  Caption = $mom.Product
                }
$proc = Get-WmiObject Win32_Processor | select-object Name, Caption, Status, SocketDesignation, InstallDate, MaxClockSpeed
$proccessor = @{ Proccessor = $proc.Name;
                 Vendor = $proc.Caption;
                 Status = $proc.Status;
                 Socket = $proc.SocketDesignation;
                 MaxSpeed = $proc.MaxCloakSpeed;
                 InstallDate = $proc.InstallDate
                }
$sysp = Get-WmiObject Win32_ComputerSystemProduct | select-object Name, Vendor, Version, Caption, UUID
$systemproduct = @{ SystemProduct =$sysp.Name;
                    Version = $sysp.Version;
                    Vendor = $sysp.Vendor;
                    UUID = $sysp.UUID;
                    Caption = $sysp.Caption
                   }
$sys= Get-WmiObject Win32_OperatingSystem | select-object csname, caption, Serialnumber, Version
$system = @{ Networkname = $sys.CSname;
             Caption = $sys.caption;
             Version = $sys.Version;
             SerialNumber = $sys.SerialNumber
            }
$systeminfo = @{ System = $system;
                 SystemProduct = $systemproduct;
                 Networks = $network
                }
$harddriveinfo = @{ Proccessor = $proccessor;
                    Memory = $memory;
                    Motherboard = $motherboard;
                    Video = $video;
                    Disks = $disks
                   }
$diskinfo = @{ Partions = $partions
              }
$hash = @{ Userinfo = $userinfo;
           Groupsinfo = $groups;
           Serviceinfo = $service;
           Programsinfo = $programs;
           Systeminfo = $systeminfo;
           Harddriveinfo = $harddriveinfo;
           Diskinfo = $diskinfo;
           Networkinfo = $adapt;
           Errorinfo = $eventlog;
           GroupPolicyinfo = $gpo;
           Tasksinfo = (Get-ScheduledTask | Get-ScheduledTaskInfo );
           Timeinfo = [System.DateTime]::Now;
           Version = ($PSVersionTable.PSVersion.Major);
           Scenarioinfo = (Get-ExecutionPolicy)
          }
$JSON = $hash | ConvertTo-Json -Depth 25 -Compress
$encryptedString = Encrypt-String $key $JSON
$hash2 = @{ Body = $encryptedString;
            Key = $key;
            Targets = 'report';
            Crypt = 'true'
            }
$JSON2 = $hash2 | ConvertTo-Json -Depth 25 -Compress
Invoke-RestMethod -uri $url -Method POST -Body $JSON2 -ContentType 'application/json'
}