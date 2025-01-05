import csv
import html

def GetParticipantsFromCSV(csvfile: str):
    participants = []
    with open(csvfile, encoding='utf-8') as csvFile:
        for row in csv.DictReader(csvFile):
            if row["Status"] != "paid":
                continue
            try:
                firstName = html.escape(row["Given name"])
                familyName = html.escape(row["Family name"])
            except KeyError:
                full_name = row["Name"].split()
                firstName = html.escape(full_name[0])
                familyName = html.escape(" ".join(full_name[1:]))
            company = html.escape(row['Company'])
            ## Job title is missing on the CSV
            # jobTitle = html.escape(row["Job"])
            jobTitle = ""
            # payment = int(float(row["Order total"]))
            # if payment > 2500:
            #     job_title = "Business"
            # elif payment == 700:
            #     job_title = "Student"
            ## sinc there is no differenciation on the ticket type, 
            ## send all as business
            ticketType = row.get("ticket_type", "")
            print(f"{firstName} {familyName} from {company} at {ticketType} as {jobTitle}")
            participants.append({
                "first_name": firstName,
                "last_name": familyName,
                "company": company,
                "ticket_type": ticketType,
                "job_title": jobTitle
            })
    return participants

def resetParticipantsData():
    return []

def numberOfParticipants(participantsList):
    return len(participantsList)

