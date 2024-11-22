import jinja2
import sendgrid
import json
import os
import argparse
import random
from dotenv import load_dotenv

def load_guests(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        guests = json.load(file)
    return guests

def shuffle_guests(guests):
    guest_list = list(guests.items())
    random.shuffle(guest_list)
    return guest_list

def create_pairs(guest_list):
    pairs = [(guest_list[i], guest_list[(i + 1) % len(guest_list)]) for i in range(len(guest_list))]
    return pairs

def send_email(api_key, from_email, to_email, subject, content):
    sg = sendgrid.SendGridAPIClient(api_key)
    from_email = sendgrid.helpers.mail.From(from_email)
    to_email = sendgrid.helpers.mail.To(to_email)
    content = sendgrid.helpers.mail.Content("text/html", content)
    mail = sendgrid.helpers.mail.Mail(from_email, to_email, subject, content)
    response = sg.send(mail)
    if response.status_code != 202:
        raise Exception(f"Failed to send email to {to_email}: {response.status_code} {response.body}")
    return response

def render_template(template_path, context):
    with open(template_path, 'r') as file:
        template = jinja2.Template(file.read())
    return template.render(context)

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description='Amigo Secreto')
    parser.add_argument('--guests', type=str, default='convidados.json', help='Path to the guests JSON file')
    parser.add_argument('--template', type=str, default='email.html', help='Path to the email template file')
    parser.add_argument('--from_email', type=str, required=True, help='Sender email address')
    parser.add_argument('--subject', type=str, default='Amigo Secreto', help='Email subject')
    args = parser.parse_args()

    api_key = os.getenv('SENDGRID_API_KEY')
    header_image = os.getenv('HEADER_IMAGE')
    if not api_key:
        raise ValueError("SendGrid API key not found in environment variables")

    guests = load_guests(args.guests)
    shuffled_guests = shuffle_guests(guests)
    pairs = create_pairs(shuffled_guests)
    random.shuffle(pairs)

    for (giver_name, giver_email), (receiver_name, receiver_email) in pairs:
        print(f'Enviando email para {giver_name} <{giver_email}>')
        context = {
            'header_image': header_image,
            'giver': giver_name,
            'receiver': receiver_name
        }
        email_content = render_template(args.template, context)
        response = send_email(api_key, args.from_email, giver_email, args.subject, email_content)

if __name__ == '__main__':
    main()