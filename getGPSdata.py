##########################################################################
##
## Read log file from Sprinkler Data of Garmin GPS on (USB)Serial Port
##
## Then convert it to GPS Coordinates, GPS Date & Time
##
#import datetime
#import time
#from datetime import datetime
#from datetime import timedelta
from datetime import date, timedelta
import subprocess

readlogfile = '/var/log/gps0.log'
count = 0
hourcorrect = +1

## For Old Garmin GPS we need to correct 1024 weeks to get the correct current date
#
correctionweeks = 1024

## For Old Garmin GPS we also need to correct the year with 2000
#
correctionyear = 2000

# open file in read mode and check how many lines are in the log file
# it can be that the log has been rotated and there is no data avaible.
#
# We need at least 7 lines of data to let this script run
#
with open(readlogfile, 'r') as fp:
    for count, line in enumerate(fp):
        pass
    count = count + 1

if (count > 7):
    with open(readlogfile, 'r') as f:
        lines = f.read().splitlines()
        counting = -7
        while counting < 0:
            last_line = lines[(counting)]

            print (counting, ":", last_line)

            if (last_line.find('$GPGGA') != -1):
                ##
                ## Found $GPGGA GPS Tag for time and position Data
                ##
                print ("###################################################################################################")
                print ("## Found $GPGGA: UTC Time, latitude, North/South, Longtitude, East/West, Satallites Used, HDOP, MSL Altitude, Unit, Geoid Seperation, Units, Age off diff., Diff. Ref station ID, Checksum")
                print ("###################################################################################################")

                splitdata = last_line.split(",")

                tijd = (splitdata[1])

                uur = int(tijd[0:2])
                minuten = int(tijd[2:4])
                seconden = int(tijd[4:6])

                lattitude = (splitdata[2])
                northsouth = (splitdata[3])
                longtitude = (splitdata[4])
                eastwest = (splitdata[5])
                nrsat = (splitdata[6])

                print ("Tijd :", tijd, " --> Uur :", uur, " / Minuten :", minuten, " / Seconden :", seconden)
            elif (last_line.find('$GPRMC') != -1):
                ##
                ## Found $GPRMC GPS Tag for time and position Data
                ##
                print ("###################################################################################################")
                print ("## Found $GPRMC: UTC Time, Status Valid/Invalid, latitude, North/South, Longtitude, East/West, Knots, Degrees, Date (Needs to be corrected), Magnetic Variation (East/West), Mode, Checksum")
                print ("###################################################################################################")

                splitdata = last_line.split(",")

                datastatus = (splitdata[2])
                datum = (splitdata[9])

                dag = int(datum[0:2])
                maand = int(datum[2:4])
                jaar = int(datum[4:6])

                print ("Datum :", datum, " --> Dag :", dag, " / Maand :", maand, " / Jaar :", jaar)
            else:
                print ("$GPGGA = MISSING! & $GPRMC = MISSING!")
            counting = counting +1

        ## Calculate date & Time
        #
        if (jaar != ""):
            #datumtijd = jaar, "-", maand, "-", dag, " ", uur, ":", minuten, ":", seconden
            #datumtijd = "2002-12-19 12:03:44"
            hetjaar = jaar

            if (hetjaar < 100):
                hetjaar = hetjaar + correctionyear

            #if (len(hetjaar) < 2):
            #    hetjaar = "0{hetjaar}"
            #
            #if (len(hetjaar) < 4):
            #    hetjaar = "20{hetjaar}"

            datumtijd = f"{jaar}-{maand}-{dag} {uur}:{minuten}:{seconden}"

            strdatumtijd = str(datumtijd)
            print ("STRDatumTijd :", strdatumtijd)
            #dt = datetime.strptime(strdatumtijd, '%Y-%m-%d %H:%M:%S')
            #print ("DatumTijd :", dt)

            #hetjaar = 2023
            #nieuwjaar = int(hetjaar)

            #print (type(hetjaar))

            date1 = date(int(hetjaar), maand, dag)
            date2 = date1 + timedelta(weeks=correctionweeks)
            print ("Calculated Date: ", date2)

            ## Calculate Time
            uur = uur + hourcorrect
            print ("Corrected Time --> uur: ", uur, "minuten: ", minuten, "seconden: ", seconden)

            ## Handle the date
            #
            cmddatum = str(date2)
            cmdjaar, cmdmaand, cmddag = cmddatum.split('-')
            cmdjaar = cmdjaar[2:4]
            print ("Laatste 2 getallen van het jaar: ", cmdjaar)
            print ("Maand: ", cmdmaand)
            print ("Dag: ", cmddag)

            ## Add Leading Zero's: https://www.geeksforgeeks.org/how-to-add-leading-zeros-to-a-number-in-python/
            #
            cli_str = f"date {cmdjaar}{cmdmaand}{cmddag}{uur:02d}{minuten:02d}.{seconden:02d}"
            print ("Command Line: ", cli_str)

            ## Execute command line with Python
            subprocess.run(cli_str, shell=True)

            print ("Lattide: ", lattitude)
            print ("NorthSouth: ", northsouth)
            print ("Longtitude: ", longtitude)
            print ("EastWest: ", eastwest)
            print ("NrSat: ", nrsat)

else:
    print ("Not enough data in: ", readlogfile, " --> There are ", count, " lines detected")

#############################################################################
##
## You also need a crontab job:
## ----------------------------
## # m h  dom mon dow   command
##
## 05,35  *  *   *   *     /usr/local/bin/checkcu.sh
##
## checkcu.sh
## -----------
## cat /usr/local/bin/checkcu.sh
## !/usr/local/bin/bash
##
## LogFile='/var/log/gps0.log'
## MinSizeLog=30
## MAXAGE=$(bc <<< '5*60') # seconds in 5 minutes
## ScriptLogFile='/var/log/startstopgps0.log'
## snelheid=4800
## dt=$(date '+%d/%m/%Y %H:%M:%S');
##
## msg="Date & Time of Check CU Running script: "+$dt+"..."
## echo -e "\e[1;0m " + $msg
## echo $msg >> $ScriptLogFile
##
## msg="Check if cu -l /dev/gsp0 -s 4800 is still running......."
## echo -e "\e[1;0m " + $msg
## echo $msg >> $ScriptLogFile
##
## mfs=$(stat -f %z $LogFile)
## if [ ${mfs} -gt $MinSizeLog ]
## then
##   # File size is good, go on with the script
##   #
##   msg="File Size of Logfile: "+$LogFile+" = "+${mfs}+" Bytes is larger than the minimum: "+$MinSizeLog+" and that is good"
##   echo -e "\e[1;0m " + $msg
##   echo $msg >> $ScriptLogFile
##
##   vandaag=$(($(date +%s)))
##   bestanddatum=$(stat -f %m "$LogFile")
##   FILEAGE=$((vandaag-bestanddatum))
##
##   test $FILEAGE -gt $MAXAGE && {
##     ## Log file is older than 5 minutes, run the script
##     #
##
##     msg="Log file is older than 5 minutes... Stop and start the cu -l /dev/gps0 -s 4800 script again"
##     echo -e "\e[1;0m " + $msg
##     echo $msg >> $ScriptLogFile
##
##     # Get the PID of cu and kill it
##     #
##     programcu=$(pgrep -x cu)
##     /bin/kill -s HUP $programcu
##
##     msg="Kill process cu with PID: "+$programcu+" and restart cu -l /dev/gps0 -s "+$snelheid+" again to create a new logfile @: "+$LogFile+" ...."
##     echo -e "\e[1;0m " + $msg
##     echo $msg >> $ScriptLogFile
##
##     /usr/bin/cu -l /dev/cuau0 -s $snelheid > $LogFile
##   }
## else
##   # File size is too small, stop cu and start it again.
##   #
##   msg="Log file is older than 5 minutes... Stop and start the cu -l /dev/gps0 -s 4800 script again"
##   echo -e "\e[1;0m " + $msg
##   echo $msg >> $ScriptLogFile
##
##   # Get the PID of cu and kill it
##   #
##   programcu=$(pgrep -x cu)
##   /bin/kill -s HUP $programcu
##
##   msg="Kill process cu with PID: "+$programcu+" and restart cu -l /dev/gps0 -s "+$snelheid+" again to create a new
##  logfile @: "+$LogFile+" ...."
##   echo -e "\e[1;0m " + $msg
##   echo $msg >> $ScriptLogFile
##
##   /usr/bin/cu -l /dev/cuau0 -s $snelheid > $LogFile
## fi
