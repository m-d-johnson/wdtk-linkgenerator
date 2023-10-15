import json
from time import sleep

from utils import send_email


def generate_problem_reports():
    dataset = json.load(open("data/generated-dataset.json", "r"))
    report_output_file = open("output/report-missing_data.txt", "w")
    report_markdown_file = open("output/missing-data.md", "w")
    # confirm = input(
    #     "This will send emails to a number of people. Is this what you want? "
    #     "Type 'Yes' to continue"
    # )
    confirm = "no"
    if confirm != "Yes":
        print("Not sending emails")
    else:
        print("Will send emails, Ctrl+C in next 10s to cancel")
        sleep(10)

    # 1: Missing Publication Scheme and Disclosure Log
    report_markdown_file.write("## Missing Pub. Scheme and Disclosure Log\n\n")
    report_markdown_file.write("|Name|Org Page|Email|\n")
    report_markdown_file.write("|-|-|-|\n")
    for force in dataset:
        if (
                force["Is_Defunct"] is False
                and len(force["Publication_Scheme_URL"]) < 10
                and len(force["Disclosure_Log_URL"]) < 10
        ):
            addressee = force["FOI_Email_Address"]
            messagebody = (
                f"Subject: Publication Scheme and Disclosure Log "
                f"URLs for {force['Name']}\n\nDear Data Protection "
                f"Officer,\n\nI have noticed that on the "
                f"WhatDoTheyKnow website {force['WDTK_Org_Page_URL']} that your "
                f"organisation is missing a link to your FOI "
                f"Publication Scheme and Disclosure Log. While I'm "
                f"aware that some information is technically "
                f"exempt from FOI Disclosure on the grounds that "
                f"it is  available on the internet, I wonder if "
                f"you'd be kind enough to send me the links to "
                f"both, please?\n\nWith thanks,\nMike "
                f"Johnson\nmdj@mikejohnson.xyz\n"
            )
            findingtxt = f"1: {force['Name']} is missing Pub Scheme URLs {force['WDTK_Org_Page_URL']}\n"
            findingmd = f"|{force['Name']} | {force['WDTK_Org_Page_URL']}|{force['FOI_Email_Address']}|\n"

            print(findingtxt)
            report_output_file.write(findingtxt)
            report_markdown_file.write(findingmd)

            if confirm == "Yes":
                print(f"Sending email to {addressee}")
                send_email(addressee, messagebody)
            else:
                print("Email sending not confirmed. Written to log anyway.")
    report_markdown_file.write("\n\n")

    # 2: Missing Disclosure Log URL but Publication Scheme present
    report_markdown_file.write("## Missing Disclosure Log only\n\n")
    report_markdown_file.write("|Name|Org Page|Email|\n")
    report_markdown_file.write("|-|-|-|\n")
    for force in dataset:
        if (
                force["Is_Defunct"] is False
                and len(force["Publication_Scheme_URL"]) > 10
                and len(force["Disclosure_Log_URL"]) < 10
        ):
            addressee = force["FOI_Email_Address"]
            messagebody = (
                f"Subject: Disclosure Log URLs for "
                f"{force['Name']}\n\nDear Data Protection Officer,\n\nI have "
                f"noticed that on the WhatDoTheyKnow website "
                f"{force['WDTK_Org_Page_URL']} that your organisation is "
                f"missing a link to your FOI Disclosure Log. While I'm aware "
                f"that some information is technically exempt from FOI "
                f"Disclosure on the grounds that it is  available on the "
                f"internet, I wonder if you'd be kind enough to send me the "
                f"link, please?\n\nWith thanks,\nMike "
                f"Johnson\nmdj@mikejohnson.xyz\n"
            )
            findingtxt = f"2: {force['Name']} is missing Disclosure Log {force['WDTK_Org_Page_URL']}\n"
            findingmd = f"|{force['Name']} | {force['WDTK_Org_Page_URL']}|{force['FOI_Email_Address']}|\n"
            print(findingtxt)
            report_output_file.write(findingtxt)
            report_markdown_file.write(findingmd)
            if confirm == "Yes":
                print(f"Sending email to {addressee}")
                send_email(addressee, messagebody)
            else:
                print("Email sending not confirmed. Written to log anyway.")
    report_markdown_file.write("\n\n")

    # 3: Missing Pubscheme URL but Disclosure Log present
    report_markdown_file.write("## Report on missing Pubscheme fields\n\n")
    report_markdown_file.write("|Name|Org Page|Email|\n")
    report_markdown_file.write("|-|-|-|\n")
    for force in dataset:
        if (
                force["Is_Defunct"] is False
                and len(force["Publication_Scheme_URL"]) < 10
                and len(force["Disclosure_Log_URL"]) > 10
        ):
            addressee = force["FOI_Email_Address"]
            messagebody = (
                f"Subject: Publication URL for {force['Name']}\n\n"
                f"Dear Data Protection Officer,\n"
                f"I have noticed that on the WhatDoTheyKnow "
                f"website {force['WDTK_Org_Page_URL']} that your "
                f"organisation is missing a link to your FOI "
                f"Publication Scheme. While I'm conscious that some "
                f"information is technically exempt from FOI "
                f"Disclosure on the grounds that it is  available "
                f"on the internet, I wonder if you'd be kind "
                f"enough to send me the link, please?\n\nWith "
                f"thanks,\nMike Johnson\nmdj@mikejohnson.xyz\n"
            )
            findingtxt = f"3: {force['Name']} is missing Pubscheme but has Disclosure Log {force['WDTK_Org_Page_URL']}\n"
            findingmd = f"|{force['Name']} | {force['WDTK_Org_Page_URL']}|{force['FOI_Email_Address']}|\n"
            print(findingtxt)
            report_output_file.write(findingtxt)
            report_markdown_file.write(findingmd)
            if confirm == "Yes":
                print(f"Sending email to {addressee}")
                send_email(addressee, messagebody)
            else:
                print("Email sending not confirmed. Written to log anyway.")
    report_markdown_file.write("\n\n")
