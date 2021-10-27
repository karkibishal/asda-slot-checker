# Script to check available delivery slots from ASDA and send an email notification

## The script will:
- Log in to the ASDA webpage, navigate to delivery slots page and retreive delivery slot information (Using selenium and chrome webriver.Username and password needs to be set in the script)
- Parse the delivery slot html and save the slots data (using beautifulsoup)
- Send email with all available time slots if found (Using yagmail. Username and password for the sender gmail account needs to be provided in the script)
