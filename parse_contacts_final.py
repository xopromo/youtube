#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import glob
import html
from collections import defaultdict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

# Dictionary to store participant info
participants = {}

# Regex patterns
tg_link_pattern = r'href="(https://t\.me/[\w\-]+)"'
phone_pattern = r'(?:\+7|8)?[\s\-]?(?:\(\d{1,4}\)|\d{3})[\s\-]?\d{2,4}[\s\-]?\d{2,4}'
email_pattern = r'[\w\.\-+]+@[\w\.\-]+\.\w+'
instagram_pattern = r'(?:https?://)?(?:www\.)?instagram\.com/([\w\._\-]+)'
website_pattern = r'https?://(?:www\.)?([a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,})'
greeting_hashtag_pattern = r'#[пП]риветствие|#[пП]ривет'

html_files = sorted(glob.glob('messages*.html'), key=lambda x: int(x.replace('messages', '').replace('.html', '') or 0))
print(f"Found {len(html_files)} HTML files")

for file_idx, html_file in enumerate(html_files):
    try:
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Find all message blocks with from_name and text
        message_pattern = r'<div class="from_name">\s*(.*?)\s*</div>.*?<div class="text">\s*(.*?)\s*</div>'

        for match in re.finditer(message_pattern, content, re.DOTALL):
            from_name_html = match.group(1)
            msg_text_html = match.group(2)

            # Clean from_name (remove HTML tags)
            from_name = re.sub(r'<[^>]+>', '', from_name_html).strip()

            # Skip empty or service messages
            if not from_name or len(from_name) < 2:
                continue

            # Clean message text
            msg_text = html.unescape(re.sub(r'<[^>]+>', '', msg_text_html)).strip()

            # Initialize participant if new
            if from_name not in participants:
                participants[from_name] = {
                    'name': from_name,
                    'tg_username': '',
                    'tg_link': '',
                    'phone': set(),
                    'email': set(),
                    'website': set(),
                    'instagram': set(),
                    'location': '',
                    'message_count': 0,
                    'sample_message': '',
                    'greeting_message': ''
                }

            participants[from_name]['message_count'] += 1

            # Check if this is a greeting message
            if re.search(greeting_hashtag_pattern, msg_text_html, re.IGNORECASE):
                # Store the greeting message (only the first one found)
                if not participants[from_name]['greeting_message'] and len(msg_text) > 10:
                    participants[from_name]['greeting_message'] = msg_text

            # Extract Telegram link from message (mentions)
            tg_links = re.findall(tg_link_pattern, msg_text_html)
            if tg_links:
                for link in tg_links:
                    username = link.split('/')[-1]
                    if not participants[from_name]['tg_username']:
                        participants[from_name]['tg_username'] = username
                        participants[from_name]['tg_link'] = link

            # Extract contacts from message text
            if msg_text:
                # Phone
                phones = re.findall(phone_pattern, msg_text)
                participants[from_name]['phone'].update(phones)

                # Email
                emails = re.findall(email_pattern, msg_text)
                participants[from_name]['email'].update(emails)

                # Instagram
                instas = re.findall(instagram_pattern, msg_text)
                participants[from_name]['instagram'].update(instas)

                # Websites
                websites = re.findall(website_pattern, msg_text)
                participants[from_name]['website'].update(websites)

                # Location
                if not participants[from_name]['location']:
                    if 'Дубай' in msg_text or 'Dubai' in msg_text:
                        participants[from_name]['location'] = 'Dubai'
                    elif 'Москв' in msg_text or 'МСК' in msg_text:
                        participants[from_name]['location'] = 'Moscow'
                    elif 'СПб' in msg_text or 'Петербург' in msg_text:
                        participants[from_name]['location'] = 'St. Petersburg'

                # Sample message (prefer non-greeting)
                if not participants[from_name]['sample_message'] and len(msg_text) > 5 and not re.search(greeting_hashtag_pattern, msg_text_html, re.IGNORECASE):
                    participants[from_name]['sample_message'] = msg_text[:100]

        if (file_idx + 1) % 50 == 0:
            print(f"  Processed {file_idx + 1}/{len(html_files)} files, {len(participants)} participants, {sum(1 for p in participants.values() if p['greeting_message'])} with greetings")

    except Exception as e:
        print(f"Error in {html_file}: {str(e)[:40]}")

print(f"\n✅ Extracted data for {len(participants)} unique participants")
print(f"   - With greeting messages: {sum(1 for p in participants.values() if p['greeting_message'])}")

# Create Excel workbook
wb = Workbook()
ws = wb.active
ws.title = "Club500 Directory"

# Headers
headers = [
    '№',
    'ФИ / Имя',
    'Приветственное сообщение',
    'Telegram Username',
    'Telegram Profile Link',
    'Телефоны',
    'Email',
    'Сайты',
    'Instagram',
    'Город',
    'Активность (сообщений)'
]

# Add header row
for col_num, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col_num)
    cell.value = header
    cell.font = Font(bold=True, color="FFFFFF")
    cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="top", wrap_text=True)

# Sort by message count
sorted_participants = sorted(participants.items(), key=lambda x: x[1]['message_count'], reverse=True)

# Add data
row_num = 2
for idx, (name, info) in enumerate(sorted_participants, 1):
    ws.cell(row=row_num, column=1).value = idx
    ws.cell(row=row_num, column=2).value = name
    ws.cell(row=row_num, column=3).value = info['greeting_message']
    ws.cell(row=row_num, column=4).value = info['tg_username']
    ws.cell(row=row_num, column=5).value = info['tg_link']
    ws.cell(row=row_num, column=6).value = ', '.join(info['phone']) if info['phone'] else ''
    ws.cell(row=row_num, column=7).value = ', '.join(info['email']) if info['email'] else ''
    ws.cell(row=row_num, column=8).value = ', '.join(info['website']) if info['website'] else ''
    ws.cell(row=row_num, column=9).value = ', '.join(info['instagram']) if info['instagram'] else ''
    ws.cell(row=row_num, column=10).value = info['location']
    ws.cell(row=row_num, column=11).value = info['message_count']

    # Format cells
    for col in range(1, 12):
        ws.cell(row=row_num, column=col).alignment = Alignment(wrap_text=True, vertical="top")

    row_num += 1

# Column widths
ws.column_dimensions['A'].width = 5
ws.column_dimensions['B'].width = 25
ws.column_dimensions['C'].width = 60
ws.column_dimensions['D'].width = 20
ws.column_dimensions['E'].width = 28
ws.column_dimensions['F'].width = 18
ws.column_dimensions['G'].width = 25
ws.column_dimensions['H'].width = 28
ws.column_dimensions['I'].width = 25
ws.column_dimensions['J'].width = 15
ws.column_dimensions['K'].width = 12

# Set row height for better readability of greeting messages
ws.row_dimensions[1].height = 30

# Freeze header
ws.freeze_panes = "A2"

# Save
wb.save('full_club500_directory.xlsx')
print(f"✅ Saved to full_club500_directory.xlsx\n")
print(f"Statistics:")
print(f"  Total participants: {len(participants)}")
print(f"  With greeting messages: {sum(1 for p in participants.values() if p['greeting_message'])}")
print(f"  With phone: {sum(1 for p in participants.values() if p['phone'])}")
print(f"  With email: {sum(1 for p in participants.values() if p['email'])}")
print(f"  With TG username: {sum(1 for p in participants.values() if p['tg_username'])}")
print(f"  With Instagram: {sum(1 for p in participants.values() if p['instagram'])}")
print(f"  With website: {sum(1 for p in participants.values() if p['website'])}")
