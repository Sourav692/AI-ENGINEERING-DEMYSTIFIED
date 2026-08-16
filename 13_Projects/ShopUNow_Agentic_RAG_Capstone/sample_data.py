"""
Sample Data for ShopUNow Agentic AI Assistant - Capstone Project
================================================================
Generated using the prompt template pattern from the capstone project guidelines.

Prompt Template Used:
---------------------
Act as an expert in running the <DEPARTMENT> department for Company ShopUNow
which is a retail company dealing in clothing, DIY, books, and toys.

Create a list of 15 Questions and Answers that are frequently asked by
<internal employees / external customers> to the <DEPARTMENT> department.

The <DEPARTMENT> department handles <DESCRIPTION>.

Return the output as a list of Python dictionaries with 'doc' and 'category'
as keys where:
- doc = "Question: <question>\nAnswer: <answer>"
- category = '<DEPARTMENT>'

Departments:
- HR (Internal Employees)
- IT Support (Internal Employees)
- Facilities & Admin (Internal Employees)
- Customer Service (External Customers)
- Product & Sales (External Customers)
- Billing & Payments (External Customers)
- Shipping & Delivery (External Customers)
"""

# ============================================================
# DEPARTMENT 1: HR (Internal Employees)
# ============================================================
hr_data = [
    {
        "doc": "Question: How many paid leaves am I entitled to per year at ShopUNow?\nAnswer: Full-time employees at ShopUNow are entitled to 24 paid leaves per year, which includes 12 casual leaves, 6 sick leaves, and 6 earned leaves. Leaves are credited at the beginning of each calendar year. Unused earned leaves can be carried forward up to a maximum of 30 days.",
        "category": "HR"
    },
    {
        "doc": "Question: What is the process to apply for maternity or paternity leave?\nAnswer: Maternity leave at ShopUNow is 26 weeks for the first two children as per the Maternity Benefit Act. Paternity leave is 2 weeks. You need to apply through the HRMS portal at least 8 weeks before your expected due date, attach the relevant medical certificate, and get approval from your reporting manager. HR will confirm the leave dates within 3 business days.",
        "category": "HR"
    },
    {
        "doc": "Question: When is the salary credited each month?\nAnswer: Salaries at ShopUNow are credited on the last working day of each month. If the last working day falls on a bank holiday, the salary is credited on the preceding working day. Your payslip is available on the HRMS portal within 2 days of salary credit.",
        "category": "HR"
    },
    {
        "doc": "Question: How do I update my bank account details for salary transfer?\nAnswer: To update your bank account details, log into the HRMS portal and navigate to 'My Profile' > 'Bank Details'. Upload a cancelled cheque or bank statement as verification. The change request will be reviewed by the payroll team and updated within 5 business days. You will receive a confirmation email once the update is processed.",
        "category": "HR"
    },
    {
        "doc": "Question: What is the performance appraisal cycle at ShopUNow?\nAnswer: ShopUNow follows an annual performance appraisal cycle. The cycle runs from April to March. Self-appraisals are due by April 15th, manager reviews by April 30th, and calibration meetings happen in May. Final ratings and increments are communicated by June 15th. Mid-year reviews happen in October for goal tracking and feedback.",
        "category": "HR"
    },
    {
        "doc": "Question: How can I enroll in the company health insurance plan?\nAnswer: All full-time employees are automatically enrolled in the group health insurance plan covering self, spouse, and up to 2 dependent children. The base coverage is INR 5 lakhs. You can opt for a top-up plan of INR 10 lakhs or INR 15 lakhs at a subsidized premium deducted from your salary. Enrollment for top-up plans opens every January. Contact hr-benefits@shopunow.com for details.",
        "category": "HR"
    },
    {
        "doc": "Question: What is the work-from-home policy at ShopUNow?\nAnswer: ShopUNow follows a hybrid work model. Corporate office employees can work from home up to 2 days per week (Wednesday and Friday are designated WFH days). Store and warehouse employees are required to be on-site. WFH requests beyond the standard policy require manager approval and HR notification through the HRMS portal.",
        "category": "HR"
    },
    {
        "doc": "Question: How do I submit my investment proofs for tax declaration?\nAnswer: Investment proofs for tax declaration must be submitted through the HRMS portal under 'Tax Declaration' section between January 1st and January 31st each year. Upload scanned copies of receipts for LIC premiums, PPF deposits, home loan certificates, rent receipts, and other eligible deductions under Section 80C, 80D, and HRA. The payroll team will adjust TDS from February salary onwards.",
        "category": "HR"
    },
    {
        "doc": "Question: What is the notice period for resignation at ShopUNow?\nAnswer: The standard notice period at ShopUNow is 60 days for all confirmed employees. During the probation period, the notice period is 30 days. You can request early release by applying for notice period buyout, which requires approval from your department head and HR. The buyout amount is calculated based on your gross salary for the remaining notice period days.",
        "category": "HR"
    },
    {
        "doc": "Question: Does ShopUNow offer any employee referral bonus?\nAnswer: Yes, ShopUNow has an active Employee Referral Program. Referral bonuses range from INR 10,000 to INR 50,000 depending on the role level. The bonus is paid in two installments — 50% after the referred candidate completes 3 months and 50% after 6 months. Refer candidates through the 'Referrals' section on the HRMS portal.",
        "category": "HR"
    },
    {
        "doc": "Question: How do I apply for an internal job transfer to another department?\nAnswer: Internal job postings are listed on the HRMS portal under 'Internal Opportunities'. You must have completed at least 12 months in your current role to be eligible. Apply through the portal and inform your current manager. HR will coordinate the interview process with the hiring department. Transfer decisions are communicated within 3 weeks of application.",
        "category": "HR"
    },
    {
        "doc": "Question: What are the company holidays for this year?\nAnswer: ShopUNow observes 12 fixed company holidays per year including Republic Day, Independence Day, Gandhi Jayanti, Diwali (2 days), Christmas, New Year, Holi, Eid, Good Friday, and 2 regional holidays based on your office location. The complete holiday calendar is published on the HRMS portal at the start of each year and also sent via email.",
        "category": "HR"
    },
    {
        "doc": "Question: How can I access my previous months' payslips?\nAnswer: You can access all your payslips from the HRMS portal. Navigate to 'Payroll' > 'Payslips' and select the month and year. Payslips are available for download in PDF format for the current and all previous financial years of your employment. If you face any issues, contact payroll@shopunow.com.",
        "category": "HR"
    },
    {
        "doc": "Question: What training and development programs does ShopUNow offer?\nAnswer: ShopUNow offers multiple L&D initiatives including: ShopUNow Academy (online courses on retail, leadership, and tech skills), quarterly skill workshops, an annual learning budget of INR 25,000 per employee for external certifications, and a mentorship program. Browse available programs on the HRMS portal under 'Learning & Development' or contact ld@shopunow.com.",
        "category": "HR"
    },
    {
        "doc": "Question: What is the policy for reporting workplace harassment or grievances?\nAnswer: ShopUNow has a zero-tolerance policy for workplace harassment. You can report incidents through the following channels: (1) Email the Internal Complaints Committee at icc@shopunow.com, (2) Use the anonymous grievance form on the HRMS portal, or (3) Speak directly to your HR Business Partner. All complaints are investigated confidentially within 10 working days. The company strictly follows the POSH Act guidelines.",
        "category": "HR"
    },
]


# ============================================================
# DEPARTMENT 2: IT Support (Internal Employees)
# ============================================================
it_support_data = [
    {
        "doc": "Question: How do I reset my ShopUNow email password?\nAnswer: To reset your email password, go to https://password.shopunow.com and click 'Forgot Password'. Enter your employee ID and registered mobile number to receive an OTP. After verification, you can set a new password. Passwords must be at least 12 characters with uppercase, lowercase, numbers, and special characters. If you are locked out, raise a ticket on the IT helpdesk portal or call ext. 5555.",
        "category": "IT Support"
    },
    {
        "doc": "Question: How do I connect to the company VPN for remote work?\nAnswer: Download the FortiClient VPN application from the IT self-service portal at https://itportal.shopunow.com/downloads. Install it and configure the VPN server address as vpn.shopunow.com. Use your employee ID and network password to connect. For first-time setup, you need to enroll in Multi-Factor Authentication (MFA) through the Authenticator app. Detailed setup guides are available on the IT portal.",
        "category": "IT Support"
    },
    {
        "doc": "Question: My laptop is running very slow. What should I do?\nAnswer: First, try restarting your laptop and closing unnecessary applications. Clear your browser cache and temporary files. Ensure your system is up-to-date by running Windows Update or macOS Software Update. If the issue persists, raise a ticket on the IT helpdesk portal under 'Hardware Issues' > 'Performance'. The IT team will run remote diagnostics or schedule an in-person check within 24 hours.",
        "category": "IT Support"
    },
    {
        "doc": "Question: How do I request a new software installation on my work laptop?\nAnswer: Submit a software request through the IT self-service portal under 'Software Requests'. Provide the software name, version, business justification, and manager approval. Standard approved software (MS Office, Slack, Zoom, etc.) is auto-provisioned within 4 hours. Non-standard software requires IT security review and takes 3-5 business days for approval.",
        "category": "IT Support"
    },
    {
        "doc": "Question: How do I set up my company email on my mobile phone?\nAnswer: ShopUNow uses Microsoft 365 for email. On your mobile device, download the Microsoft Outlook app from the App Store or Google Play. Open the app, enter your work email (employeeid@shopunow.com), and authenticate using your network credentials and MFA. The company MDM (Mobile Device Management) policy will be applied automatically. Personal email apps are not supported for security reasons.",
        "category": "IT Support"
    },
    {
        "doc": "Question: I accidentally deleted an important file. Can it be recovered?\nAnswer: If the file was stored on OneDrive or SharePoint, check the Recycle Bin within the respective application — deleted files are retained for 93 days. For files on your local machine, check the system Recycle Bin. If the file was permanently deleted, raise an urgent IT ticket with the file path and approximate deletion time. Our backup system retains data for 30 days and recovery takes 24-48 hours.",
        "category": "IT Support"
    },
    {
        "doc": "Question: How do I access the company Wi-Fi at ShopUNow offices?\nAnswer: Connect to the Wi-Fi network named 'ShopUNow-Corp' using your employee ID and network password. For guest access (visitors or personal devices), connect to 'ShopUNow-Guest' and register through the captive portal using your employee ID as the sponsor. Guest access is limited to internet only and expires after 8 hours. Store locations use the 'ShopUNow-Store' network.",
        "category": "IT Support"
    },
    {
        "doc": "Question: How do I raise an IT support ticket?\nAnswer: You can raise IT support tickets through three channels: (1) IT Self-Service Portal at https://itportal.shopunow.com — log in with your employee ID, (2) Email ithelp@shopunow.com with a detailed description, or (3) Call the IT helpdesk at ext. 5555 for urgent issues. Tickets are categorized by priority — Critical (1 hour SLA), High (4 hours), Medium (1 business day), Low (3 business days).",
        "category": "IT Support"
    },
    {
        "doc": "Question: How do I get access to shared drives and team folders?\nAnswer: Access to shared drives is managed through your department's access groups. Your manager can request access for you by raising a ticket on the IT portal under 'Access Management' > 'Shared Drives'. Provide the drive or folder path and the level of access needed (read-only or read-write). Access is provisioned within 4 hours after manager approval.",
        "category": "IT Support"
    },
    {
        "doc": "Question: What should I do if I suspect a phishing email?\nAnswer: Do NOT click any links or download attachments from the suspicious email. Forward the email as an attachment to security@shopunow.com. Then mark the email as phishing in Outlook by clicking 'Report Message' > 'Phishing'. The IT security team will analyze the email and take necessary action. If you accidentally clicked a link, immediately change your password and report it as a critical IT ticket.",
        "category": "IT Support"
    },
    {
        "doc": "Question: How do I request a replacement for my damaged laptop or peripherals?\nAnswer: Raise a ticket on the IT portal under 'Hardware Requests' > 'Replacement'. Attach photos of the damage and provide a brief description. Your manager's approval is required for replacements. Standard peripherals (keyboard, mouse, headset) are replaced within 2 business days. Laptop replacements take 5-7 business days. The damaged equipment must be returned to the IT asset team.",
        "category": "IT Support"
    },
    {
        "doc": "Question: How can I access ShopUNow systems while traveling internationally?\nAnswer: Before traveling, inform IT by raising a travel request on the IT portal at least 5 days in advance with your destination country and travel dates. Some countries require special VPN configurations due to local internet restrictions. Ensure MFA is set up on your mobile device before departure. Use only the company VPN for accessing internal systems. Avoid connecting to public Wi-Fi without VPN.",
        "category": "IT Support"
    },
    {
        "doc": "Question: How do I set up multi-factor authentication (MFA)?\nAnswer: MFA is mandatory for all ShopUNow employees. Download the Microsoft Authenticator app on your phone. Go to https://aka.ms/mfasetup, sign in with your work credentials, and follow the prompts to scan the QR code with the Authenticator app. You can also set up a backup phone number for SMS verification. MFA setup must be completed within your first week of joining.",
        "category": "IT Support"
    },
    {
        "doc": "Question: Can I use my personal USB drive on the company laptop?\nAnswer: No, personal USB drives are blocked by the company's endpoint security policy to prevent data leakage and malware risks. If you need to transfer files, use OneDrive, SharePoint, or the company's approved file transfer tool. For exceptional cases requiring USB access (e.g., vendor demos), raise a security exception request on the IT portal with business justification and manager approval.",
        "category": "IT Support"
    },
    {
        "doc": "Question: How do I book a conference room with video conferencing equipment?\nAnswer: Conference rooms are booked through Microsoft Outlook calendar. Create a new meeting, click 'Add Room', and search for available rooms by location and capacity. Rooms with video conferencing are tagged with 'VC' in the name (e.g., 'Mumbai-Floor3-VC-01'). The Zoom/Teams equipment in VC rooms starts automatically when a meeting is scheduled. For technical issues during meetings, call the IT helpdesk at ext. 5555.",
        "category": "IT Support"
    },
]


# ============================================================
# DEPARTMENT 3: Customer Service (External Customers)
# ============================================================
customer_service_data = [
    {
        "doc": "Question: How can I track my order from ShopUNow?\nAnswer: You can track your order by logging into your ShopUNow account at www.shopunow.com and navigating to 'My Orders'. Click on the specific order to see real-time tracking updates including dispatch, in-transit, out-for-delivery, and delivered status. You will also receive SMS and email notifications at each stage. For any tracking concerns, contact our support at support@shopunow.com or call 1800-SHOP-NOW.",
        "category": "Customer Service"
    },
    {
        "doc": "Question: What is ShopUNow's return and refund policy?\nAnswer: ShopUNow offers a 30-day easy return policy for most products. Clothing and accessories can be returned within 30 days if unused with original tags. DIY tools and books can be returned within 15 days if unopened and in original packaging. Toys can be returned within 15 days if defective. To initiate a return, go to 'My Orders' > select the item > 'Return/Replace'. Refunds are processed within 5-7 business days to your original payment method.",
        "category": "Customer Service"
    },
    {
        "doc": "Question: How do I cancel an order that has already been placed?\nAnswer: You can cancel your order before it is shipped by going to 'My Orders' on the ShopUNow website or app, selecting the order, and clicking 'Cancel Order'. If the order has already been shipped, you can refuse delivery or initiate a return once delivered. Cancellation refunds are processed within 3-5 business days. For prepaid orders, the amount is refunded to your original payment method. For COD orders, no charge is applied.",
        "category": "Customer Service"
    },
    {
        "doc": "Question: I received a damaged or defective product. What should I do?\nAnswer: We apologize for the inconvenience. Please report the issue within 48 hours of delivery by going to 'My Orders' > select the item > 'Report Issue' > 'Damaged/Defective'. Upload photos of the damaged product and packaging. Our team will verify and arrange a free replacement or full refund within 2 business days. You can also reach us at support@shopunow.com with your order ID and photos.",
        "category": "Customer Service"
    },
    {
        "doc": "Question: What payment methods does ShopUNow accept?\nAnswer: ShopUNow accepts a wide range of payment methods including: Credit/Debit Cards (Visa, Mastercard, RuPay, Amex), Net Banking (all major banks), UPI (Google Pay, PhonePe, Paytm), ShopUNow Wallet, EMI options (no-cost EMI on select products), and Cash on Delivery (COD) for orders up to INR 10,000. Gift cards and ShopUNow reward points can also be used at checkout.",
        "category": "Customer Service"
    },
    {
        "doc": "Question: How do I apply a promo code or discount coupon at checkout?\nAnswer: During checkout on the ShopUNow website or app, you will see an 'Apply Coupon' field on the payment page. Enter your promo code and click 'Apply'. The discount will be reflected in the order summary. Note that only one coupon can be applied per order, and coupons cannot be combined with ongoing sale prices unless specified. Check 'Offers' section on the homepage for latest active coupons.",
        "category": "Customer Service"
    },
    {
        "doc": "Question: Does ShopUNow offer free shipping?\nAnswer: Yes! ShopUNow offers free standard shipping on all orders above INR 499. Orders below INR 499 have a flat shipping charge of INR 49. Express delivery (1-2 business days) is available at INR 99 for metro cities and INR 149 for other locations. ShopUNow Premium members enjoy free express shipping on all orders with no minimum purchase requirement.",
        "category": "Customer Service"
    },
    {
        "doc": "Question: How long does delivery take for ShopUNow orders?\nAnswer: Standard delivery takes 4-7 business days depending on your location. Metro cities (Mumbai, Delhi, Bangalore, Chennai, Hyderabad, Kolkata) typically receive orders in 3-5 business days. Express delivery is available for 1-2 business day delivery in metro cities. Remote locations may take up to 10 business days. Delivery timelines are shown at checkout based on your pincode.",
        "category": "Customer Service"
    },
    {
        "doc": "Question: How do I create an account on ShopUNow?\nAnswer: Visit www.shopunow.com and click 'Sign Up' in the top right corner. You can register using your email address, mobile number, or sign up directly with your Google or Facebook account. Enter your name, email, mobile number, and create a password. Verify your account via the OTP sent to your mobile number. Once verified, you can start shopping and enjoy member-exclusive deals.",
        "category": "Customer Service"
    },
    {
        "doc": "Question: How do I contact ShopUNow customer support?\nAnswer: You can reach ShopUNow customer support through multiple channels: (1) Phone: Call 1800-SHOP-NOW (toll-free, available 8 AM - 10 PM, 7 days a week), (2) Email: support@shopunow.com (response within 24 hours), (3) Live Chat: Available on the website and app during business hours, (4) WhatsApp: Message us at +91-9876543210, (5) Social Media: DM us on Twitter @ShopUNow_Help or Facebook @ShopUNow.",
        "category": "Customer Service"
    },
    {
        "doc": "Question: Can I exchange a product for a different size or color?\nAnswer: Yes, exchanges are available for clothing and accessories within 30 days of delivery. Go to 'My Orders' > select the item > 'Exchange'. Choose the new size or color from available options. The exchange pickup and delivery is free of charge. If the desired size/color is out of stock, you can opt for a full refund instead. Exchange deliveries typically arrive within 5-7 business days.",
        "category": "Customer Service"
    },
    {
        "doc": "Question: How does ShopUNow's loyalty rewards program work?\nAnswer: ShopUNow Rewards is our loyalty program where you earn 1 reward point for every INR 10 spent. Points can be redeemed at checkout — 100 points = INR 10 discount. You automatically earn Silver status (2x points) after spending INR 10,000 in a year, Gold (3x points) after INR 25,000, and Platinum (5x points) after INR 50,000. Points expire after 12 months of inactivity. Check your points balance in 'My Account' > 'Rewards'.",
        "category": "Customer Service"
    },
    {
        "doc": "Question: Is it safe to shop on ShopUNow? How is my data protected?\nAnswer: Absolutely! ShopUNow uses 256-bit SSL encryption for all transactions. We are PCI-DSS compliant and never store your full card details on our servers. All payment processing is handled through certified payment gateways. Your personal data is protected under our privacy policy in compliance with applicable data protection regulations. We never share your data with third parties without consent.",
        "category": "Customer Service"
    },
    {
        "doc": "Question: I received the wrong product in my order. What should I do?\nAnswer: We're sorry about the mix-up. Please report this within 48 hours by going to 'My Orders' > select the item > 'Report Issue' > 'Wrong Product Received'. Upload a photo of the product you received. We will arrange a free pickup of the wrong product and deliver the correct item within 3-5 business days. If the correct product is unavailable, we'll issue a full refund. No need to worry — we've got you covered!",
        "category": "Customer Service"
    },
    {
        "doc": "Question: Does ShopUNow offer gift wrapping or personalized messages?\nAnswer: Yes! Gift wrapping is available for INR 49 per item. During checkout, select 'Add Gift Wrap' next to the item. You can also include a personalized message of up to 150 characters on a gift card included in the package. Gift-wrapped orders do not include the price tag or invoice. For bulk gifting (corporate orders of 10+ items), contact corporategifts@shopunow.com for special rates.",
        "category": "Customer Service"
    },
]


# ============================================================
# DEPARTMENT 4: Product & Sales (External Customers)
# ============================================================
product_sales_data = [
    {
        "doc": "Question: What types of products does ShopUNow sell?\nAnswer: ShopUNow is a retail company offering a wide range of products across four major categories: (1) Clothing — men's, women's, and kids' apparel including ethnic wear, casual wear, formal wear, and sportswear, (2) DIY (Do It Yourself) — tools, home improvement kits, craft supplies, and garden equipment, (3) Books — fiction, non-fiction, academic, children's books, and e-books, (4) Toys — educational toys, board games, action figures, outdoor play equipment, and STEM kits.",
        "category": "Product & Sales"
    },
    {
        "doc": "Question: Are the products on ShopUNow original and authentic?\nAnswer: Yes, ShopUNow guarantees 100% authentic and original products. We source directly from brands and authorized distributors. Every product on our platform comes with an authenticity guarantee. If you ever receive a product that you suspect is not genuine, report it immediately through 'My Orders' and we will investigate, arrange a return, and issue a full refund. Look for the 'ShopUNow Assured' badge for verified products.",
        "category": "Product & Sales"
    },
    {
        "doc": "Question: How often does ShopUNow have sales or discount events?\nAnswer: ShopUNow runs several major sale events throughout the year: ShopUNow Republic Day Sale (January), Summer Splash Sale (April-May), Monsoon Madness (July), Back to School Sale (August), The Big ShopUNow Festive Sale (October - our biggest sale during Diwali), Black Friday Sale (November), and Year-End Clearance (December). Flash sales happen every weekend. Subscribe to our newsletter and enable app notifications to never miss a deal!",
        "category": "Product & Sales"
    },
    {
        "doc": "Question: Can I buy products in bulk or wholesale from ShopUNow?\nAnswer: Yes, ShopUNow offers a B2B bulk ordering program called 'ShopUNow Business'. Businesses can register at business.shopunow.com to access wholesale pricing, bulk discounts (10-30% off depending on quantity), GST invoicing, and dedicated account management. Minimum bulk order is 25 units per SKU. For corporate gifting needs, contact corporatesales@shopunow.com or call our B2B helpline at 1800-SHOP-B2B.",
        "category": "Product & Sales"
    },
    {
        "doc": "Question: Does ShopUNow have physical retail stores I can visit?\nAnswer: Yes! ShopUNow operates 150+ retail stores across India in major cities including Mumbai, Delhi NCR, Bangalore, Chennai, Hyderabad, Kolkata, Pune, and Ahmedabad. Our stores carry curated selections from all categories. Use the 'Store Locator' on our website or app to find the nearest store, check store hours, and see available inventory. Many stores also offer 'Buy Online, Pick Up In-Store' (BOPIS) service.",
        "category": "Product & Sales"
    },
    {
        "doc": "Question: How can I check if a product is available in my size or preferred color?\nAnswer: On each product page, available sizes and colors are displayed with real-time stock information. If your preferred size or color shows 'Out of Stock', click the 'Notify Me' button and enter your email. We'll alert you as soon as it's restocked. You can also check availability at nearby physical stores using the 'Check In-Store Availability' option on the product page.",
        "category": "Product & Sales"
    },
    {
        "doc": "Question: Does ShopUNow offer any warranty on DIY tools and electronics?\nAnswer: Yes, all DIY tools and electronic products sold on ShopUNow come with the manufacturer's warranty. Warranty periods vary by product — typically 1 year for power tools, 6 months for hand tools, and 1-2 years for electronic accessories. Warranty details are mentioned on each product page under 'Warranty Information'. To claim warranty, contact the brand's service center or raise a ticket on ShopUNow with your order ID and proof of purchase.",
        "category": "Product & Sales"
    },
    {
        "doc": "Question: Can I pre-order upcoming or out-of-stock products?\nAnswer: Yes, ShopUNow offers a pre-order option for select upcoming product launches and popular items that are temporarily out of stock. Look for the 'Pre-Order' button on the product page. A small booking amount (typically 10-20% of the price) is charged at the time of pre-order, and the remaining is charged upon dispatch. Pre-order items are shipped on the specified launch or restock date shown on the product page.",
        "category": "Product & Sales"
    },
    {
        "doc": "Question: How do I find the right size when shopping for clothing online?\nAnswer: Each clothing product on ShopUNow includes a detailed 'Size Guide' with measurements in inches and centimeters. Click the 'Size Guide' link on the product page for brand-specific size charts. We also offer a 'Virtual Fit' tool powered by AI — upload your measurements and get personalized size recommendations. If you're between sizes, we recommend choosing the larger size. Easy exchanges are available if the fit isn't right.",
        "category": "Product & Sales"
    },
    {
        "doc": "Question: What age groups are ShopUNow's toys suitable for?\nAnswer: ShopUNow offers toys for all age groups with clear age recommendations on each product: (1) 0-2 years: soft toys, sensory toys, rattles, (2) 3-5 years: building blocks, art kits, picture books, (3) 6-8 years: board games, STEM kits, outdoor play sets, (4) 9-12 years: science kits, model building, strategy games, (5) 13+ years: complex puzzles, robotics kits, hobby tools. Each product page displays the recommended age range and safety certifications.",
        "category": "Product & Sales"
    },
    {
        "doc": "Question: Does ShopUNow sell eco-friendly or sustainable products?\nAnswer: Yes! ShopUNow has a dedicated 'Green ShopUNow' collection featuring eco-friendly products across all categories. This includes organic cotton clothing, sustainable fashion brands, eco-friendly DIY supplies, recycled paper books, and non-toxic wooden toys. Look for the green leaf icon on product listings. We also use recyclable packaging for all shipments and offer a packaging return program at our physical stores.",
        "category": "Product & Sales"
    },
    {
        "doc": "Question: Can I write and read product reviews on ShopUNow?\nAnswer: Absolutely! After receiving your order, you'll get an email prompting you to review the product. You can rate from 1-5 stars, write a text review, and upload photos. Reviews from verified purchasers are marked with a 'Verified Purchase' badge. All reviews are moderated for appropriateness. Top reviewers earn ShopUNow Rewards points. Browse reviews on any product page under the 'Ratings & Reviews' section.",
        "category": "Product & Sales"
    },
    {
        "doc": "Question: Does ShopUNow offer any subscription boxes?\nAnswer: Yes! ShopUNow offers curated subscription boxes: (1) 'BookBox' — 2 books monthly based on your genre preferences (INR 599/month), (2) 'KidBox' — age-appropriate toys and activities monthly (INR 999/month), (3) 'StyleBox' — 3-5 clothing items curated by stylists (INR 1,999/month with free returns), (4) 'DIY Maker Box' — monthly project kits (INR 799/month). Subscribe at www.shopunow.com/subscriptions. First month is 50% off for all boxes!",
        "category": "Product & Sales"
    },
    {
        "doc": "Question: How do I find products on sale or with discounts?\nAnswer: There are several ways to find deals on ShopUNow: (1) Visit the 'Deals of the Day' section on the homepage for daily discounts up to 70% off, (2) Check the 'Clearance' section for end-of-season sales, (3) Use price filters and sort by 'Discount: High to Low' in any category, (4) Enable push notifications for flash sale alerts, (5) Follow us on social media for exclusive coupon codes. ShopUNow Premium members get early access to all sales.",
        "category": "Product & Sales"
    },
    {
        "doc": "Question: Does ShopUNow ship internationally?\nAnswer: Currently, ShopUNow ships across all pincodes within India including remote areas. International shipping is available to select countries — UAE, USA, UK, Canada, Singapore, and Australia — through our 'ShopUNow Global' service. International orders have a flat shipping rate of INR 1,500 (or equivalent) for orders under INR 5,000 and free shipping above INR 5,000. Delivery takes 7-15 business days. Custom duties, if applicable, are borne by the customer.",
        "category": "Product & Sales"
    },
]


# ============================================================
# DEPARTMENT 5: Facilities & Admin (Internal Employees)
# ============================================================
facilities_admin_data = [
    {
        "doc": "Question: How do I book a meeting room or conference hall at ShopUNow offices?\nAnswer: Meeting rooms can be booked through the ShopUNow Facilities Portal at https://facilities.shopunow.com or via the Outlook calendar integration. Search by office location, floor, capacity (4-seater, 8-seater, boardroom), and available time slots. Bookings can be made up to 2 weeks in advance. No-show bookings (not checked in within 15 minutes) are auto-released. For large events or town halls requiring the auditorium, email facilities@shopunow.com at least 5 business days in advance.",
        "category": "Facilities & Admin"
    },
    {
        "doc": "Question: How do I request a new employee ID card or replace a lost one?\nAnswer: For new joiners, ID cards are issued on Day 1 during onboarding by the Facilities team. If your ID card is lost, damaged, or stolen, raise a request on the Facilities Portal under 'ID Card' > 'Replacement'. A temporary access pass will be issued within 2 hours. The replacement permanent ID card takes 3-5 business days. There is a replacement fee of INR 200 deducted from salary. Report stolen cards immediately to security@shopunow.com.",
        "category": "Facilities & Admin"
    },
    {
        "doc": "Question: What are the office working hours at ShopUNow?\nAnswer: Standard office working hours at ShopUNow corporate offices are 9:30 AM to 6:30 PM, Monday to Friday. Flexible timing is available with core hours between 10:30 AM and 4:30 PM — you can start anytime between 8:30 AM and 10:30 AM. Warehouse and store employees follow shift-based schedules as communicated by their managers. Office access is available 24/7 with valid ID card for employees who need to work late.",
        "category": "Facilities & Admin"
    },
    {
        "doc": "Question: How do I report a maintenance issue in the office (AC, lights, plumbing, etc.)?\nAnswer: Report maintenance issues on the Facilities Portal under 'Maintenance Request'. Select the issue type (electrical, plumbing, HVAC, furniture, cleaning), office location, and floor. Attach a photo if possible. Priority issues like water leaks, electrical hazards, or broken lifts are addressed within 2 hours. Routine maintenance (flickering lights, AC temperature, loose furniture) is addressed within 1 business day. For emergencies, call the facilities helpline at ext. 4444.",
        "category": "Facilities & Admin"
    },
    {
        "doc": "Question: Is there a cafeteria or pantry facility in ShopUNow offices?\nAnswer: Yes, all ShopUNow corporate offices have a subsidized cafeteria managed by a third-party vendor. Breakfast (8:30-10:00 AM), lunch (12:30-2:00 PM), and evening snacks (4:30-5:30 PM) are served daily. Meals are subsidized at 50% by the company. Each floor also has a pantry with complimentary tea, coffee, water dispensers, and a microwave. The cafeteria menu is published weekly on the Facilities Portal. Special dietary requests can be submitted to cafeteria@shopunow.com.",
        "category": "Facilities & Admin"
    },
    {
        "doc": "Question: How do I get a parking spot at the ShopUNow office?\nAnswer: Parking is available on a first-come-first-served basis at most ShopUNow offices. For regular parking allocation, apply through the Facilities Portal under 'Parking' > 'Monthly Pass'. Monthly parking passes cost INR 500 for two-wheelers and INR 1,500 for four-wheelers, deducted from salary. Visitor parking can be pre-booked by employees for their guests. EV charging stations are available in the basement at select offices.",
        "category": "Facilities & Admin"
    },
    {
        "doc": "Question: How do I request office supplies like stationery, notebooks, or printer cartridges?\nAnswer: Office supplies can be ordered through the Facilities Portal under 'Stationery & Supplies'. Select items from the approved catalog — pens, notepads, staplers, sticky notes, printer paper, toner cartridges, etc. Orders placed before 2 PM are delivered to your desk by next business day. Each department has a monthly stationery budget. Bulk or non-standard items require manager approval. For urgent needs, visit the Admin desk on the ground floor.",
        "category": "Facilities & Admin"
    },
    {
        "doc": "Question: What is the process for requesting office furniture or ergonomic equipment?\nAnswer: All employees are provided standard workstation furniture (desk, chair, monitor stand). If you need ergonomic equipment like a standing desk, ergonomic chair, footrest, or wrist rest, submit a request on the Facilities Portal under 'Furniture & Ergonomics'. Requests supported by a medical certificate are prioritized and fulfilled within 5 business days. Standard ergonomic assessments are conducted by the Facilities team quarterly — you can sign up on the portal.",
        "category": "Facilities & Admin"
    },
    {
        "doc": "Question: How do I arrange for visitor access to the ShopUNow office?\nAnswer: Pre-register your visitor on the Facilities Portal under 'Visitor Management' at least 24 hours in advance. Provide the visitor's name, company, purpose of visit, and date/time. The visitor will receive an SMS with a QR code for entry. On arrival, visitors must present the QR code at reception and collect a visitor badge. Visitors must be escorted by the host employee at all times. Visitor access is limited to common areas and designated meeting rooms.",
        "category": "Facilities & Admin"
    },
    {
        "doc": "Question: Does ShopUNow provide transport or cab facilities for employees?\nAnswer: ShopUNow provides subsidized cab service for employees working late (after 8:30 PM) or early morning shifts (before 7:00 AM). Book through the 'ShopUNow Rides' app or Facilities Portal at least 2 hours before your required pickup time. The company covers 80% of the fare within a 25 km radius. For regular commute, ShopUNow partners with shuttle bus services on select routes — check route availability on the Facilities Portal under 'Transport'.",
        "category": "Facilities & Admin"
    },
    {
        "doc": "Question: What fire safety and emergency evacuation procedures should I know?\nAnswer: ShopUNow conducts mandatory fire drills every quarter. Emergency exits are marked with green signs on every floor. In case of fire: (1) Do NOT use elevators, (2) Proceed to the nearest emergency exit, (3) Assemble at the designated muster point in the parking area, (4) Report to your floor warden for headcount. Fire extinguishers are located at every stairwell and pantry. Emergency contact: Security Control Room ext. 9999. New employees receive fire safety training during onboarding week.",
        "category": "Facilities & Admin"
    },
    {
        "doc": "Question: How do I request a seating change or relocation to a different floor?\nAnswer: Seating arrangements are managed by the Facilities team in coordination with department heads. To request a change, raise a ticket on the Facilities Portal under 'Seating' > 'Relocation Request'. Provide the reason (team restructuring, noise concerns, project-based seating, etc.) and preferred location. Requests are reviewed weekly and accommodated based on availability. Department-level relocations are coordinated with HR and respective managers.",
        "category": "Facilities & Admin"
    },
    {
        "doc": "Question: Is there a gym or wellness facility at ShopUNow offices?\nAnswer: Select ShopUNow offices (Mumbai HQ, Bangalore Tech Park, Delhi NCR) have an on-site fitness center with gym equipment, yoga room, and shower facilities. Access is free for all employees — register at the gym reception with your employee ID. Operating hours are 6:30 AM to 9:30 PM. Yoga and meditation sessions are conducted Tuesdays and Thursdays at 7:00 AM. Other offices have tie-ups with nearby gyms at discounted corporate rates — check the Facilities Portal for details.",
        "category": "Facilities & Admin"
    },
    {
        "doc": "Question: How do I dispose of old electronics or e-waste at the office?\nAnswer: ShopUNow follows responsible e-waste disposal practices. Do NOT throw electronic items (old keyboards, mice, chargers, batteries, cables) in regular dustbins. Drop them in the designated e-waste bins located near the IT asset counter on the ground floor. For large items (old monitors, printers), raise a ticket on the Facilities Portal under 'E-Waste Disposal'. The Facilities team coordinates quarterly e-waste drives with certified recyclers.",
        "category": "Facilities & Admin"
    },
    {
        "doc": "Question: What should I do if I find a lost item or lose something in the office?\nAnswer: If you find a lost item, please hand it over to the reception desk or Security office on the ground floor. If you've lost something, check with reception first or raise a request on the Facilities Portal under 'Lost & Found'. Describe the item, last known location, and date. The security team will check CCTV footage if needed. Found items are held for 30 days. Unclaimed items after 30 days are donated to charity. You'll receive an email notification if your item is found.",
        "category": "Facilities & Admin"
    },
]


# ============================================================
# DEPARTMENT 6: Billing & Payments (External Customers)
# ============================================================
billing_payments_data = [
    {
        "doc": "Question: My payment was deducted but the order was not confirmed. What should I do?\nAnswer: Sometimes payments take a few minutes to be verified. Please wait 30 minutes and check your order status under 'My Orders'. If the order still shows as 'Payment Pending' or is not visible, the amount will be auto-refunded to your original payment method within 5-7 business days. If the refund is not received after 7 days, contact us at billing@shopunow.com with your transaction reference number, bank statement screenshot, and order ID (if available).",
        "category": "Billing & Payments"
    },
    {
        "doc": "Question: How do I get a GST invoice for my ShopUNow purchase?\nAnswer: To receive a GST invoice, add your GSTIN during checkout in the 'Business/GST Details' section. The GST invoice will be generated automatically and available for download under 'My Orders' > select order > 'Download Invoice'. If you forgot to add GSTIN during checkout, raise a request within 48 hours at billing@shopunow.com with your order ID and GSTIN. Please note that GST invoices cannot be generated after the return window has closed.",
        "category": "Billing & Payments"
    },
    {
        "doc": "Question: What EMI options are available on ShopUNow?\nAnswer: ShopUNow offers EMI on orders above INR 3,000. Options include: (1) No-Cost EMI on select products (3, 6, or 9 months) with participating bank credit cards, (2) Standard EMI (3-24 months) on all major bank credit cards with applicable interest, (3) Bajaj Finserv EMI Card for cardless EMI, (4) ShopUNow Pay Later — buy now and pay in 3 interest-free installments. EMI options are displayed on the product page and at checkout.",
        "category": "Billing & Payments"
    },
    {
        "doc": "Question: How do I check the status of my refund?\nAnswer: To check your refund status, go to 'My Orders' > select the returned/cancelled order > 'Refund Status'. The timeline depends on the payment method: UPI refunds take 1-3 business days, credit/debit card refunds take 5-7 business days, net banking refunds take 3-5 business days, and wallet refunds are instant. You'll receive an email and SMS when the refund is initiated and when it's credited. For delays beyond the stated timeline, contact billing@shopunow.com.",
        "category": "Billing & Payments"
    },
    {
        "doc": "Question: Can I change the payment method after placing an order?\nAnswer: Payment method cannot be changed after an order is confirmed and paid. However, for Cash on Delivery (COD) orders that haven't been shipped yet, you can switch to prepaid by going to 'My Orders' > 'Pay Now' within 24 hours. If you need to change the payment method, you can cancel the order (before shipment) and place a new one with the preferred payment method. No cancellation charges apply for prepaid orders.",
        "category": "Billing & Payments"
    },
    {
        "doc": "Question: How does ShopUNow Wallet work and how do I add money to it?\nAnswer: ShopUNow Wallet is a prepaid digital wallet for faster checkouts. Add money via UPI, net banking, or debit card — minimum INR 100, maximum balance INR 10,000. Wallet balance is used automatically at checkout (you can uncheck it). Refunds for wallet-paid orders are credited instantly to the wallet. Promotional cashback is also credited to the wallet. Wallet balance cannot be transferred to a bank account. Manage your wallet under 'My Account' > 'ShopUNow Wallet'.",
        "category": "Billing & Payments"
    },
    {
        "doc": "Question: I was charged twice for the same order. How do I get a resolution?\nAnswer: Double charges sometimes occur due to payment gateway glitches. Do not worry — duplicate charges are automatically detected and refunded within 3-5 business days. If the duplicate charge is not reversed within 5 days, email billing@shopunow.com with: (1) Order ID, (2) Transaction reference numbers for both charges, (3) Bank statement showing the double debit. Our billing team will escalate it with the payment gateway and resolve within 48 hours.",
        "category": "Billing & Payments"
    },
    {
        "doc": "Question: How do I redeem a ShopUNow gift card?\nAnswer: To redeem a gift card, go to checkout and click 'Apply Gift Card'. Enter the 16-digit gift card code and the 4-digit PIN (found on the back of physical cards or in the email for e-gift cards). The balance will be applied to your order. If the order value exceeds the gift card balance, pay the remaining amount using another payment method. Gift cards are valid for 12 months from the date of purchase. Check balance at 'My Account' > 'Gift Cards'.",
        "category": "Billing & Payments"
    },
    {
        "doc": "Question: Does ShopUNow charge any convenience fee for Cash on Delivery (COD)?\nAnswer: ShopUNow charges a nominal COD handling fee of INR 29 per order. This fee covers the operational cost of cash collection at your doorstep. The COD fee is displayed at checkout before you confirm the order. COD is available for orders up to INR 10,000. For higher-value orders, please use prepaid payment methods. ShopUNow Premium members are exempt from the COD convenience fee.",
        "category": "Billing & Payments"
    },
    {
        "doc": "Question: How do I download my purchase invoice or receipt?\nAnswer: Invoices are auto-generated for all orders. Go to 'My Orders' > select the order > click 'Download Invoice' to get a PDF copy. The invoice includes order details, item-wise pricing, applicable taxes, shipping charges, and discounts applied. For GST-registered businesses, the invoice includes GSTIN details. Invoices are also sent to your registered email within 24 hours of order confirmation. For consolidated invoices (multiple orders), contact billing@shopunow.com.",
        "category": "Billing & Payments"
    },
    {
        "doc": "Question: What should I do if my promo code or discount is not being applied at checkout?\nAnswer: If your promo code isn't working, check the following: (1) Ensure the code hasn't expired — check the validity dates, (2) Verify minimum order value requirements are met, (3) Check if the code is applicable to the items in your cart (some codes exclude sale items or specific categories), (4) Confirm the code hasn't been already used (single-use codes). If everything checks out and it still doesn't work, take a screenshot and email offers@shopunow.com with the code details. Our team will assist within 24 hours.",
        "category": "Billing & Payments"
    },
    {
        "doc": "Question: Can I get a price adjustment if an item I purchased goes on sale within a few days?\nAnswer: ShopUNow offers a 7-day Price Protection Guarantee. If the price of an item you purchased drops within 7 days of your order date, you can claim the difference. Go to 'My Orders' > select the order > 'Price Match Request'. The price difference will be credited to your ShopUNow Wallet within 3 business days. This applies only to items sold by ShopUNow directly (not marketplace sellers) and excludes flash sales and clearance events.",
        "category": "Billing & Payments"
    },
    {
        "doc": "Question: How do I set up auto-pay for my ShopUNow subscription boxes?\nAnswer: For subscription services (BookBox, KidBox, StyleBox, DIY Maker Box), you can set up auto-pay during subscription signup. We support auto-pay via credit/debit card and UPI autopay mandate. Go to 'My Account' > 'Subscriptions' > 'Payment Settings' to manage your auto-pay method. You'll receive a reminder email 3 days before each charge. You can pause, cancel, or change payment method anytime before the next billing date.",
        "category": "Billing & Payments"
    },
    {
        "doc": "Question: Is there a way to split payment across multiple methods?\nAnswer: Yes! ShopUNow supports split payments. At checkout, you can combine: (1) ShopUNow Wallet balance + card/UPI, (2) Gift Card balance + card/UPI, (3) Reward Points + any payment method. However, you cannot split between two credit/debit cards or two UPI IDs in a single transaction. The wallet and gift card balance is deducted first, and the remaining amount is charged to your selected payment method.",
        "category": "Billing & Payments"
    },
    {
        "doc": "Question: What is ShopUNow Pay Later and how do I sign up?\nAnswer: ShopUNow Pay Later allows you to buy now and pay in 3 interest-free monthly installments with no additional charges. To sign up, go to 'My Account' > 'ShopUNow Pay Later' and complete a quick KYC verification (PAN card + Aadhaar). Approval is instant for most users with a credit limit up to INR 20,000. Once approved, select 'ShopUNow Pay Later' at checkout. Payments are auto-debited from your linked bank account on the 5th of each month. Late payments attract a fee of INR 100 per installment.",
        "category": "Billing & Payments"
    },
]


# ============================================================
# DEPARTMENT 7: Shipping & Delivery (External Customers)
# ============================================================
shipping_delivery_data = [
    {
        "doc": "Question: How can I track my ShopUNow delivery in real-time?\nAnswer: Once your order is shipped, you'll receive a tracking link via SMS and email. You can also track from 'My Orders' > select order > 'Track Package'. Real-time tracking shows the package journey through dispatch, in-transit, out-for-delivery, and delivered stages. For orders with our logistics partner ShopUNow Express, you get live map tracking when the delivery executive is within 5 km of your location. Tracking updates refresh every 30 minutes.",
        "category": "Shipping & Delivery"
    },
    {
        "doc": "Question: Can I change my delivery address after placing an order?\nAnswer: Address changes are possible only before the order is shipped. Go to 'My Orders' > select the order > 'Modify Address'. Once the order status changes to 'Shipped', the address cannot be modified. In that case, you can request the delivery executive to hold the package at the nearest hub by calling the number provided in your tracking SMS. Alternatively, refuse delivery and place a new order with the correct address.",
        "category": "Shipping & Delivery"
    },
    {
        "doc": "Question: What happens if I'm not available at the time of delivery?\nAnswer: If you're not available, the delivery executive will attempt to call you. If unreachable, the package will be reattempted the next business day. ShopUNow makes a total of 3 delivery attempts. After 3 failed attempts, the package is returned to the warehouse and a full refund is initiated. You can also use 'Safe Drop' (leave at door) or designate an alternate recipient in your delivery preferences under 'My Account' > 'Address Book'.",
        "category": "Shipping & Delivery"
    },
    {
        "doc": "Question: Does ShopUNow offer same-day or next-day delivery?\nAnswer: Yes! ShopUNow Express offers: (1) Same-Day Delivery — available in 6 metro cities (Mumbai, Delhi, Bangalore, Chennai, Hyderabad, Kolkata) for orders placed before 12 PM on eligible items marked with 'Same-Day' badge. Cost: INR 149. (2) Next-Day Delivery — available in 20+ cities for orders placed before 6 PM. Cost: INR 99. ShopUNow Premium members get free next-day delivery on all eligible orders.",
        "category": "Shipping & Delivery"
    },
    {
        "doc": "Question: My order shows 'Delivered' but I haven't received it. What should I do?\nAnswer: We're sorry about this. First, check with family members, neighbors, or your building security/reception as the package may have been handed to them. Check for a 'Safe Drop' photo in your tracking details. If still not found, report the issue within 48 hours through 'My Orders' > 'Report Issue' > 'Not Received'. Our logistics team will investigate with the delivery partner and resolve within 72 hours — either reship the item or issue a full refund.",
        "category": "Shipping & Delivery"
    },
    {
        "doc": "Question: Can I schedule a specific delivery date and time slot?\nAnswer: Yes, ShopUNow offers scheduled delivery in select cities. During checkout, choose 'Schedule Delivery' and pick your preferred date (up to 7 days out) and time slot: Morning (9 AM - 12 PM), Afternoon (12 PM - 3 PM), Evening (3 PM - 6 PM), or Night (6 PM - 9 PM). Scheduled delivery is available for a nominal fee of INR 29. ShopUNow Premium members can schedule deliveries for free.",
        "category": "Shipping & Delivery"
    },
    {
        "doc": "Question: Does ShopUNow deliver to PO Boxes or APO/military addresses?\nAnswer: ShopUNow delivers to all valid Indian postal addresses including PO Boxes. For defense and military cantonments, delivery depends on the specific location's accessibility to our logistics partners. Enter your pincode on the product page to check serviceability. Remote and island locations (Andaman & Nicobar, Lakshadweep) may have extended delivery timelines of 12-15 business days and limited COD availability.",
        "category": "Shipping & Delivery"
    },
    {
        "doc": "Question: How is my package packed to ensure it arrives safely?\nAnswer: ShopUNow uses secure, multi-layer packaging. Fragile items (DIY tools, toys) are wrapped in bubble wrap and placed in corrugated boxes with foam cushioning. Clothing is packed in moisture-resistant poly bags inside shipping boxes. Books have rigid cardboard mailers to prevent bending. All packages are sealed with tamper-evident tape. If you receive a package that appears tampered with, do not accept it and report immediately through the app.",
        "category": "Shipping & Delivery"
    },
    {
        "doc": "Question: Can I have multiple items from one order delivered to different addresses?\nAnswer: Currently, each order is delivered to a single address. If you need items shipped to different addresses, please place separate orders for each address. However, if your order contains items from different sellers or warehouses, they may arrive as separate shipments on different dates — each with its own tracking number. All shipments will be delivered to the same address specified during checkout.",
        "category": "Shipping & Delivery"
    },
    {
        "doc": "Question: What are the shipping charges for different delivery options?\nAnswer: ShopUNow shipping charges are as follows: (1) Standard Delivery (4-7 days): FREE for orders above INR 499, INR 49 for orders below INR 499, (2) Express Delivery (1-2 days): INR 99 for metro cities, INR 149 for non-metro, (3) Same-Day Delivery: INR 149 (metro cities only), (4) Scheduled Delivery: INR 29 surcharge on top of standard/express rates. ShopUNow Premium members get free standard and express delivery on all orders.",
        "category": "Shipping & Delivery"
    },
    {
        "doc": "Question: Can I pick up my order from a ShopUNow store instead of home delivery?\nAnswer: Yes! ShopUNow offers 'Click & Collect' — order online and pick up from your nearest ShopUNow store for free. Select 'Store Pickup' during checkout and choose your preferred store. You'll receive a notification when your order is ready (usually within 4-24 hours). Bring your order confirmation email/SMS and a valid ID for pickup. Orders are held at the store for 7 days. After 7 days, uncollected orders are returned and refunded.",
        "category": "Shipping & Delivery"
    },
    {
        "doc": "Question: How do I return a product? Will ShopUNow arrange the pickup?\nAnswer: To return a product, go to 'My Orders' > select the item > 'Return'. Choose your reason, and select a pickup date and time slot. ShopUNow arranges free reverse pickup from your address — our logistics partner will come to collect the item. Pack the product in its original packaging with all accessories and tags. You'll receive a confirmation once the item is picked up and another when the refund is initiated after quality check.",
        "category": "Shipping & Delivery"
    },
    {
        "doc": "Question: My package is stuck in transit for many days. What can I do?\nAnswer: If your package tracking hasn't updated for more than 48 hours, go to 'My Orders' > 'Track Package' > 'Report Delay'. Our logistics team will investigate with the delivery partner. Common reasons for delays include: weather disruptions, address-related issues, customs (for inter-state large shipments), or local delivery backlogs. You'll receive an updated ETA within 24 hours of reporting. If the package is lost in transit, we'll reship or refund within 5 business days.",
        "category": "Shipping & Delivery"
    },
    {
        "doc": "Question: Does ShopUNow use eco-friendly packaging for deliveries?\nAnswer: Yes, ShopUNow is committed to sustainable shipping. We use: (1) 100% recyclable corrugated boxes, (2) Paper-based tape instead of plastic tape, (3) Biodegradable bubble wrap and corn-starch packing peanuts, (4) Minimal packaging — right-sized boxes to reduce waste. We've eliminated single-use plastic from 95% of our shipments. Customers can opt for 'Minimal Packaging' at checkout to receive items with reduced packaging where safe to do so.",
        "category": "Shipping & Delivery"
    },
    {
        "doc": "Question: How does ShopUNow handle delivery of large or heavy items like furniture or DIY equipment?\nAnswer: Large and heavy items (above 10 kg or oversized) are delivered through our specialized logistics partners. Delivery includes: (1) Ground-floor doorstep delivery is standard and free, (2) In-room placement and basic assembly is available for INR 299 in select cities, (3) Delivery is scheduled by appointment — you'll receive a call to confirm date and 4-hour time window. Large item deliveries typically take 7-10 business days. Track large shipments separately under 'My Orders' > 'Large Items'.",
        "category": "Shipping & Delivery"
    },
]


# ============================================================
# COMBINED DATA
# ============================================================
all_data = (
    hr_data
    + it_support_data
    + facilities_admin_data
    + customer_service_data
    + product_sales_data
    + billing_payments_data
    + shipping_delivery_data
)


# ============================================================
# Utility: Print summary
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("ShopUNow - Agentic AI Assistant Sample Data")
    print("=" * 60)

    departments = {}
    for item in all_data:
        cat = item["category"]
        departments[cat] = departments.get(cat, 0) + 1

    print(f"\nTotal QA pairs: {len(all_data)}")
    print(f"\nDepartments ({len(departments)}):")
    for dept, count in departments.items():
        user_type = "Internal Employees" if dept in ["HR", "IT Support", "Facilities & Admin"] else "External Customers"
        print(f"  - {dept} ({user_type}): {count} QA pairs")

    print("\n--- Sample entries ---")
    for dept in ["HR", "IT Support", "Facilities & Admin", "Customer Service", "Product & Sales", "Billing & Payments", "Shipping & Delivery"]:
        entry = next(d for d in all_data if d["category"] == dept)
        print(f"\n[{dept}]")
        print(f"  {entry['doc'][:120]}...")
