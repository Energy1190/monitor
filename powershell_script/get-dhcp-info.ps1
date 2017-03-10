﻿$url = "http://172.16.9.71"
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
$d = Get-DhcpServerv4Lease -AllLeases -ScopeId 172.16.0.0 | select-object IPAddress, ScopeId, ClientId, HostName, AddressState, LeaseExpiryTime
$DHCP = @{ ip = $d.IPAddress;
           mac = $d.ClientId;
           scope = $d.ScopeId;
           rezervation = $d.AddressState;
           name = $d.HostName;
           timeend = $d.LeaseExpiryTime
           }
$hash = @{ Dhcpinfo = $DHCP;
           Timeinfo = [System.DateTime]::Now;
          }
$JSON = $hash | ConvertTo-Json -Depth 25 -Compress
$encryptedString = Encrypt-String $key $JSON
$hash2 = @{ Body = $encryptedString;
            Key = $key;
            Targets = 'dhcp';
            Crypt = 'true'
            }
$JSON2 = $hash2 | ConvertTo-Json -Depth 25 -Compress
Invoke-RestMethod -uri $url -Method POST -Body $JSON2 -ContentType 'application/json'
