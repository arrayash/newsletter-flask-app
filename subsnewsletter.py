import os
import time
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from urllib.parse import quote
from dotenv import load_dotenv

# NEW and CORRECT
from app import db, Subscriber, app
# --- 1. Configuration ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)  # Fixed typo here

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
APP_DOMAIN = os.getenv("APP_DOMAIN", "http://127.0.0.1:5000")
SEND_NEWSLETTER = os.getenv("SEND_NEWSLETTER", "True").lower() == "true"
TEST_RECIPIENT_EMAIL = os.getenv("TEST_RECIPIENT_EMAIL")
CC_RECIPIENT_EMAIL = os.getenv("CC_RECIPIENT_EMAIL")  # Add this to your .env file

# --- 2. Manual News Content ---

def get_manual_news_articles():
    """Returns manually curated news articles organized by category."""
    logger.info("📰 Loading manually curated news articles...")

    # Regulatory Updates - FSSAI Updates & Enforcement Actions
    regulatory_updates = [
        {
            "title": "High Court seeks J&K Govt & FSSAI response on PIL ",
            "description": "The J&K High Court has sought responses on a PIL over the largest rotten meat scandal involving a seizure of 11,000 Kgs of rotten meat. Meanwhile, the state ordered strict FSSAI compliance and warned of heavy penalties for violators.",
            "url": "https://www.crosstownnews.in/post/145643/high-court-seeks-jk-govt-fssai%E2%80%99s-response-on-pil-in-4-days-over-rotten-meat-issue.html",
            "category": "Regulatory Updates"
        },
        {
            "title": "FSSAI amends labelling rules for coffee–chicory mixtures ",
            "description": "The regulator clarified blend declarations and labelling rules to improve consumer understanding.",
            "url": "https://www.legalitysimplified.com/fssai-amends-labelling-regulations-for-coffee-chicory-mixtures/",  # Removed leading space
            "category": "Regulatory Updates"
        },
        {
            "title": "Gujarat extends deadline for inputs on Food Safety Act amendments",
            "description": "Authorities have extended the deadline to allow wider stakeholder feedback on proposed changes.",
            "url": "https://ianslive.in/gujarat-govt-extends-deadline-for-suggestions-on-food-safety-act-amendments--20250820201808",
            "category": "Regulatory Updates"
        },
        {
            "title": " Bottled water: pre-licence inspections & standards—what FBOs must know",
            "description": "New guidelines explain inspection steps and standards required before bottled-water licences are issued.",
            "url": "https://www.livemint.com/news/india/food-safety-bottled-water-fssai-regulations-india-pre-licence-inspections-safety-standards-11755660019082.html",
            "category": "Regulatory Updates"
        }
    ]

    # Industry News - Food Innovation & Technology Trends
    industry_news = [
        {
            "title": "FSSAI suspends AR Dairy licence over ghee adulteration & false info ",
            "description": "The licence was revoked after officials found ghee adulteration and mislabelling.",
            "url": "https://www.livemint.com/news/fssai-suspends-ar-dairy-licence-ghee-adulteration-false-information-11755422633259.html",
            "category": "Industry News"
        },
        {
            "title": "Blue Tokai: bouncing back from a fake-licence scare to 155 outlets ",
            "description": "The coffee brand restored compliance discipline and customer trust after an early setback.",
            "url": "https://www.livemint.com/companies/news/from-cramped-delhi-room-to-155-outlets-across-india-how-blue-tokai-overcame-fssai-fake-licence-scare-to-brew-success-11755249417877.html",
            "category": "Industry News"
        },
        {
            "title": "Kerala seizes 17,000 litres of adulterated coconut oil",
            "description": "Officials uncovered a large adulteration racket in Thiruvananthapuram, protecting public health.",
            "url": "https://www.newindianexpress.com/cities/thiruvananthapuram/2025/Aug/20/17k-litres-of-adulterated-coconut-oil-seized",
            "category": "Industry News"  # Added missing category
        },
        {
            "title": "6,500 kg adulterated ghee seized in Rajkot ",
            "description": "A major seizure in Rajkot highlights ongoing enforcement against dairy adulteration.",
            "url": "https://www.zeebiz.com/india/news-fssai-seizes-6500-kg-adulterated-ghee-worth-rs-35-lakh-from-rajkot-dairy-376973",
            "category": "Industry News"
        },
        {
            "title": "Goa FDA crackdown ",
            "description": "Regulators fined chicken outlets and suspended sweet units over repeated safety violations.",
            "url": "https://www.heraldgoa.in/goa/goa/goa-fda-cracks-down-on-food-safety-violations-fines-chicken-shops-suspends-sweet-units/426316",
            "category": "Industry News"
        },
        {
            "title": "AP raids across restaurants, bakeries, hotels  ",
            "description": "Joint state teams intensified surprise checks across eateries to strengthen compliance.",
            "url": "https://www.thehindu.com/news/national/andhra-pradesh/legal-metrology-food-safety-officials-raids-on-restaurants-bakeries-hotels/article69950638.ece",
            "category": "Industry News"
        },
        {
            "title": "Jaggery adulteration case in Kerala",
            "description": "Enforcement expanded to traditional products as adulterated jaggery was detected in Kannur.",
            "url": "https://www.onmanorama.com/news/kerala/2025/08/21/jaggery-adulteration-kannur.html",
            "category": "Industry News"
        },
        {
            "title": " 1,500 street-food poisoning cases at Pune in 6 months  ",
            "description": "Poor hygiene at city stalls has caused widespread food-borne illnesses, mostly among students.",
            "url": "https://punemirror.com/city/pune/punes-street-food-crisis-1500-poisoning-cases-in-six-months-students-worst-hit/",
            "category": "Industry News"
        },
        {
            "title": " Food-testing labs in Vishakhapatnam and Thirumalai to start next month   ",
            "description": "Two new labs will expand testing infrastructure and accelerate enforcement actions.",
            "url": "https://timesofindia.indiatimes.com/city/vijayawada/food-quality-testing-labs-in-vizag-tirumala-to-start-operations-next-month/articleshow/123336628.cms",
            "category": "Industry News"
        }
    ]

    # Food Nutrition - Food Safety Violations & Health Crises
    food_nutrition = [
        {
            "title": " FSSAI–Danone India launch 'Mauli': all-women Clean Street Food Hub in Mumbai",
            "description": "The project demonstrates a replicable women-led hygiene model for safe street-food vending.",
            "url": "https://www.storyboard18.com/brand-marketing/danone-india-and-fssai-launch-mauli-an-all-women-clean-street-food-hub-79035.htm",
            "category": "Food Nutrition"
        },
        {
            "title": " FSSAI's scale plan: train 2.5 million food handlers; tighter inter-agency coordination ",
            "description": "The roadmap calls for nationwide training and stronger coordination to improve food safety.",
            "url": "https://etedge-insights.com/sdgs-and-esg/sustainability/serving-safety-at-scale-fssais-vision-to-transform-what-india-eats/",
            "category": "Food Nutrition"
        },
        {
            "title": " Mista's 'curated collaboration' to transform the food system ",
            "description": "The consortium model brings together startups and corporates to drive food innovation and safety.",
            "url": "https://www.foodbusinessnews.net/articles/28864-mista-using-curated-collaboration-to-transform-food-system",
            "category": "Food Nutrition"
        },
        {
            "title": " UPF overconsumption driven by perception: study",
            "description": "Research shows consumer perceptions strongly influence overconsumption of ultra-processed foods.",
            "url": "https://www.foodnavigator.com/Article/2025/08/20/upf-overconsumption-due-to-perception-study-claims/",
            "category": "Food Nutrition"
        },
        {
            "title": "Precision nutrition & aging: policy/industry takeaways ",
            "description": "Experts highlight how AI and multi-omics can guide healthy-aging nutrition strategies.",
            "url": "https://www.nature.com/articles/s41514-025-00266-5",
            "category": "Food Nutrition"
        }
    ]

    # International News - Global Food Safety Alerts & Market Trends
    international_news = [
        {
            "title": "Walmart recalls frozen shrimp over possible radioactive contamination of Cesium 137 ",
            "description": "The FDA flagged risks in Indonesian-sourced shrimp, prompting a nationwide recall.",
            "url": "https://www.theguardian.com/business/2025/aug/20/walmart-radioactive-shrimp-recall",
            "category": "International News"
        },
        {
            "title": "Traceability ramp-up: 30+ suppliers join ReposiTrak network ",
            "description": "Global suppliers of tea, plant-based milk, and snacks are adopting digital traceability tools.",
            "url": "https://www.businesswire.com/news/home/20250819385602/en/Tea-Plant-Based-Milk-and-Real-Food-Snack-Suppliers-Join-29-Others-Preparing-for-Food-Traceability-With-ReposiTrak",
            "category": "International News"
        },
        {
            "title": "UK FSA: low levels of antibiotic-resistant Listeria & E. coli in salmon fillets ",
            "description": "Low but detectable levels of resistant bacteria were found in salmon, underlining AMR risks.",
            "url": "https://www.food-safety.com/articles/10632-uk-fsa-reports-low-levels-of-antibiotic-resistant-listeria-e-coli-in-salmon-filets",
            "category": "International News"
        },
        {
            "title": "US FDA weighs higher orange-juice sugar limits to aid growers ",
            "description": "Regulators are considering easing sugar standards to support the citrus industry.",
            "url": "https://www.foxnews.com/food-drink/orange-juice-sugar-cuts-proposed-fda-help-citrus-growers-what-means-you",  # Removed leading space
            "category": "International News"
        },
        {
            "title": "Tyson Foods deploys AI conversational assistant for B2C search ",
            "description": "The company rolled out an AI-powered tool to enhance consumer interactions and search.",
            "url": "https://aws.amazon.com/blogs/machine-learning/tyson-foods-elevates-customer-search-experience-with-an-ai-powered-conversational-assistant/",
            "category": "International News"
        }
    ]

    # Combine all categories and return structured content
    content = {
        'regulatory_updates': regulatory_updates,
        'industry_news': industry_news,
        'international_news': international_news,
        'best_practices': food_nutrition,  # Using 'best_practices' to match your original variable name
    }

    total_articles = len(regulatory_updates) + len(industry_news) + len(food_nutrition) + len(international_news)

    logger.info(f"✅ Successfully loaded {total_articles} manually curated articles:")
    logger.info(f"   - Regulatory Updates: {len(regulatory_updates)}")
    logger.info(f"   - Industry News: {len(industry_news)}")
    logger.info(f"   - Food Nutrition: {len(food_nutrition)}")
    logger.info(f"   - Global Updates: {len(international_news)}")

    return content



# --- 3. Static Content Definition ---

def get_newsletter_content():
    """Returns ONLY the main feature static content."""
    logger.info("📖 Loading main feature content...")
    content = {
        "main_feature": {
            
            "headline": "How AI is <span style=\"color: #2CC3DA;\">Transforming</span>  Food Safety",
            "title ":"A weekly newsletter on food safety, quality & traceability from Safe2Eat Food Institute sponsored by Neophyte.ai",
            "summary": "A pivotal week for food safety: India sharpened enforcement after the J&K rotten meat scandal, with new state orders, court scrutiny, and FSSAI updates on coffee–chicory labeling and bottled-water norms. Major seizures in Kerala and Gujarat underscored rising vigilance. Globally, Walmart recalled frozen shrimp over radiation fears, the UK flagged antimicrobial resistance in salmon, and the US reviewed orange-juice standards. On a positive note, FSSAI backed a women-led clean street-food hub, while global players pushed traceability and AI to strengthen supply chains."
        }
    }
    logger.info("✅ Successfully loaded main feature content.")
    return content


# --- 4. Helper Functions for CC Functionality ---

def parse_email_list(email_string):
    """Parse comma-separated email string and return clean list."""
    if not email_string:
        return []
    return [email.strip() for email in email_string.split(',') if email.strip()]


def get_all_recipients():
    """Get main recipients and CC recipients separately."""
    main_recipients = parse_email_list(TEST_RECIPIENT_EMAIL)
    cc_recipients = parse_email_list(CC_RECIPIENT_EMAIL)
    
    # Remove duplicates between TO and CC
    cc_recipients = [email for email in cc_recipients if email not in main_recipients]
    
    return main_recipients, cc_recipients


# --- 5. HTML Generation ---

def generate_html_content(static_content, categorized_content, unsubscribe_link, subscribe_link):
    """Creates the HTML body from the main feature and categorized articles."""
    
    def create_category_section(category_title, articles, category_color, category_icon):
        """Creates HTML for a category section with its articles."""
        if not articles:
            return ""
        
        articles_html = ""
        for article in articles:
            articles_html += f"""
            <tr>
                <td style="padding-bottom: 20px; border-bottom: 1px solid #1e2d3b; padding-top: 12px;">
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                        <tr>
                            <td valign="top">
                                <h4 style="margin: 0 0 8px 0; font-family: Arial, sans-serif; font-size: 15px; line-height: 1.4; color: #FFFFFF; font-weight: bold;">{article["title"]}</h4>
                                <p style="margin: 0 0 12px 0; font-family: Arial, sans-serif; font-size: 13px; line-height: 1.6; color: #bdc5d1;">{article["description"]}</p>
                                <a href="{article["url"]}" target="_blank" style="color: #2CC3DA; text-decoration: none; font-weight: bold; font-size: 13px;">Read Article →</a>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            """
        
        return f"""
        <tr>
            <td style="padding: 25px 17px 10px 20px;">
                <h3 style="margin: 0 0 15px 0; font-family: Arial, sans-serif; font-size: 18px; color: #FFFFFF; font-weight: bold; border-left: 4px solid {category_color}; padding-left: 12px; display: flex; align-items: center;">
                    <span style="margin-right: 8px;">{category_icon}</span>{category_title}
                </h3>
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin-bottom: 20px;">
                    {articles_html}
                </table>
            </td>
        </tr>
        """

    # Category configurations
    categories_config = [
        {
            "title": "Regulatory Updates",
            "key": "regulatory_updates",
            "color": "#2CC3DA",
            "icon": ""
        },
        {
            "title": "Industry Updates", 
            "key": "industry_news",
            "color": "#2CC3DA",
            "icon": ""
        },
        {
            "title": "International Updates",
            "key": "international_news", 
            "color": "#2CC3DA",
            "icon": ""
        },
        {
            "title": "Food & Nutrition  Best Practices",
            "key": "best_practices",
            "color": "#2CC3DA", 
            "icon": ""
        }  
        
    ]

    # Generate all category sections
    news_sections_html = ""
    total_articles = 0
    
    for config in categories_config:
        articles = categorized_content.get(config["key"], [])
        total_articles += len(articles)
        section_html = create_category_section(
            config["title"], 
            articles, 
            config["color"], 
            config["icon"]
        )
        news_sections_html += section_html

    # Main feature content
    main_feature = static_content['main_feature']
    
    # Complete newsletter HTML
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Neo Safe2Eat Newsletter</title>
    </head>
    <body style="margin: 0; padding: 0; background-color: #0c1a24; font-family: Arial, sans-serif;">
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #0c1a24;">
            <tr>
                <td align="center">
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="margin: 0 auto; max-width: 600px;">
                        
                        <!-- HEADER -->
                        <tr>
                            <td style="padding: 20px 10px 10px 10px;" align="right">
                                <span style="font-family: 'Courier New', Courier, monospace; font-size: 28px; color: #e2e8f0; letter-spacing: 2px;">
                                    NE<span style="color: #2CC3DA;">O</span>PHYTE
                                </span>
                            </td>
                        </tr>
                        
                        <tr>
                            <td style="padding: 20px 0; border-top: 1px solid #1e293b; border-bottom: 1px solid #1e293b;">
                                <h1 style="margin: 0; font-family: 'Courier New', Courier, monospace; font-size: 28px; text-align: center; color: #FFFFFF; letter-spacing: 4px;">
                                    NEO <span style="color: #2CC3DA;">SAFE2EAT</span> NEWSLETTER
                                </h1>
                                <p style="margin: 10px 0 0 0; text-align: center; font-size: 12px; color: #8a94a1;">
                                     A weekly newsletter on food safety, quality & traceability from Safe2Eat Food Institute sponsored by Neophyte.ai
                                </p>
                                <p style="margin: 10px 0 0 0; text-align: center; font-size: 12px; color: #8a94a1;">Volume 1: Week 4 (Aug 16 – 22, 2025)</p>
                            </td>
                        </tr>
                        
                        <!-- MAIN FEATURE -->
                        <tr>
                            <td style="padding: 30px 20px;">
                                <h2 style="margin: 25px 0 15px 0; font-family: Arial, sans-serif; font-size: 30px; font-weight: bold; color: #FFFFFF; line-height: 1.3;">
                                    {main_feature['headline']}
                                </h2>
                                
                                <p style="margin: 0 0 20px 0; font-family: Arial, sans-serif; font-size: 14px; color: #bdc5d1; line-height: 1.6;">
                                    {main_feature['summary']}
                                </p>
                                
                                
                            </td>
                        </tr>
                        
                        <!-- NEWS BRIEFING HEADER -->
                        
                        <!-- CATEGORIZED NEWS SECTIONS -->
                        {news_sections_html}
                        
                        <!-- FOOTER -->
                        <tr>
                            <td style="padding: 30px 20px; background-color: #115e59;">
                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                    <tr>
                                        <td width="120" valign="top" style="min-width: 120px;">
                                            <p style="margin: 0 0 10px 0; font-family: Arial, sans-serif; font-size: 14px; color: #ffffff; font-weight: bold;">
                                                REACH US AT
                                            </p>
                                            <img src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=https://www.neophyte.ai" 
                                                 width="100" height="100" alt="QR Code" style="border: 1px solid #2CC3DA; display: block;">
                                        </td>
                                        <td valign="top" style="padding-left: 20px; font-family: Arial, sans-serif; font-size: 13px; color: #bdc5d1; line-height: 1.8; word-wrap: break-word;">
                                            📧 <a href="mailto:contact@neophyte.ai" style="color: #ffffff; text-decoration: none;">contact@neophyte.ai</a><br>
                                            📞 <a href="tel:+919321236115,+912235987401" style="color: #ffffff; text-decoration: none;">+91-9321236115 , +91-2235987401</a><br>
                                            🌐 <a href="https://www.neophyte.ai" style="color: #ffffff; text-decoration: none;">www.neophyte.ai</a><br>
                                            <p style="margin: 8px 0 0 0; line-height: 1.6; word-wrap: break-word;">
                                                <strong style="color: #e2e8f0;">Address:</strong> Neophyte Ambient Intelligence, 11th Floor, Office No. 1107 to 1110, Kamdhenu Commerz, Plot No. 2, Sector 14, Kharghar, Navi Mumbai, 410210, India
                                            </p>
            
                                            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #2CC3DA;">
                                                <p style="margin: 0; font-size: 11px; color: #ffffff;">
                                                    <strong>Neo Safe2Eat</strong> - Your trusted source for food safety intelligence
                                                </p>
                                            </div>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- SUBSCRIPTION SECTION IN FOOTER -->
                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin-top: 25px; border-top: 1px solid #2CC3DA; padding-top: 20px;">
                                    <tr>
                                        <td align="center">
                                            <h3 style="margin: 0 0 10px 0; font-family: Arial, sans-serif; font-size: 16px; color: #FFFFFF; font-weight: bold;">
                                                Newsletter Subscription
                                            </h3>
                                            <p style="margin: 0 0 15px 0; font-family: Arial, sans-serif; font-size: 12px; color: #bdc5d1;">
                                                Get weekly updates on food safety & quality delivered to your inbox
                                            </p>
                                            
                                            <!-- SUBSCRIPTION BUTTONS -->
                                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin: 0 auto;">
                                                <tr>
                                                    <td style="padding-right: 8px;">
                                                        <a href="{subscribe_link}" target="_blank" style="background-color: #28a745; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block; font-size: 12px; font-family: Arial, sans-serif;">
                                                             Subscribe
                                                        </a>
                                                    </td>
                                                    
                                                </tr>
                                            </table>
                                            
                                            <p style="margin: 15px 0 0 0; font-size: 10px; color: #8a94a1; line-height: 1.4;">
                                                You are receiving this newsletter because you subscribed to our food safety updates.<br>
                                                No longer want these emails? </p><a href="{unsubscribe_link}" target="_blank" style=" color:  #8a94a1; text-decoration: none; font-family: Arial, sans-serif;">
                                                             Unsubscribe here
                                                        </a>.
                                            
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


# --- 6. Enhanced Email Sending Function ---
def send_newsletter_with_cc(server, recipient_email, cc_recipients, subject, html_body, unsubscribe_link):
    """Send newsletter to a recipient with CC functionality."""
    try:
        # Create email message
        msg = MIMEMultipart("alternative")
        msg["From"] = formataddr(("Neo Safe2Eat Weekly Newsletter", EMAIL_ADDRESS))
        msg["To"] = recipient_email
        
        # Add CC recipients if any
        if cc_recipients:
            msg["Cc"] = ", ".join(cc_recipients)
        
        msg["Subject"] = subject
        
        # Add unsubscribe header
        msg.add_header("List-Unsubscribe", f"<{unsubscribe_link}>")

        # Attach HTML content
        msg.attach(MIMEText(html_body, "html"))

        # Determine all recipients (TO + CC)
        all_recipients = [recipient_email] + cc_recipients

        # Send email
        server.sendmail(EMAIL_ADDRESS, all_recipients, msg.as_string())
        
        # Log successful send
        cc_info = f" (CC: {', '.join(cc_recipients)})" if cc_recipients else ""
        logger.info(f"✅ Newsletter sent successfully to {recipient_email}{cc_info}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send email to {recipient_email}. Error: {e}")
        return False


# --- 7. Main Orchestration Function ---
def run_newsletter_campaign():
    """Orchestrates the newsletter creation and sending process with CC functionality."""
    logger.info("🚀 Starting Neo Safe2Eat Newsletter Campaign with CC Support...")

    if not SEND_NEWSLETTER:
        logger.info("SEND_NEWSLETTER is set to False in .env file. Exiting campaign.")
        return

    # Load content
    static_content = get_newsletter_content()
    categorized_content = get_manual_news_articles()
    
    # Calculate total articles
    total_articles = (
        len(categorized_content['regulatory_updates']) +
        len(categorized_content['industry_news']) +
        len(categorized_content['best_practices']) +
        len(categorized_content['international_news'])
    )
    
    # Setup recipients with CC support
    main_recipients, cc_recipients = get_all_recipients()
    
    if not main_recipients:
        logger.warning("⚠ No main recipients found. Please set TEST_RECIPIENT_EMAIL in your .env file.")
        return

    # Log recipient information
    logger.info(f"📧 Email Recipients Configuration:")
    logger.info(f"   - Main Recipients (TO): {', '.join(main_recipients)}")
    if cc_recipients:
        logger.info(f"   - CC Recipients: {', '.join(cc_recipients)}")
    else:
        logger.info(f"   - CC Recipients: None")

    # Email configuration
    subject = f"Neo Safe2Eat Weekly Newsletter Volume 1 | Week 4"

    try:
        # SMTP connection and sending
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            logger.info("✅ Logged into SMTP server successfully.")

            successful_sends = 0
            failed_sends = 0

            for email in main_recipients:
                # Generate unsubscribe and subscribe links for each recipient
                unsubscribe_link = f"{APP_DOMAIN}/unsubscribe/{quote(email, safe='')}"
                subscribe_link = f"{APP_DOMAIN}/subscribe/{quote(email, safe='')}"
                
                
                
                # Generate HTML content
                html_body = generate_html_content(static_content, categorized_content, unsubscribe_link, subscribe_link)
                
                # Send email with CC
                if send_newsletter_with_cc(server, email, cc_recipients, subject, html_body, unsubscribe_link):
                    successful_sends += 1
                else:
                    failed_sends += 1
                
                # Rate limiting
                time.sleep(1)

    except Exception as e:
        logger.error(f"❌ Failed to connect to SMTP server. Error: {e}", exc_info=True)
        return

    # Final summary
    total_unique_recipients = len(main_recipients) + len(cc_recipients)
    logger.info("🎉 Newsletter campaign finished!")
    logger.info(f"📊 Campaign Summary:")
    logger.info(f"   - Total Articles: {total_articles}")
    logger.info(f"   - Main Recipients: {len(main_recipients)}")
    logger.info(f"   - CC Recipients: {len(cc_recipients)}")
    logger.info(f"   - Total Unique Recipients: {total_unique_recipients}")
    logger.info(f"   - Successful Sends: {successful_sends}")
    logger.info(f"   - Failed Sends: {failed_sends}")
    logger.info(f"   - Categories: 4 (Regulatory, Industry, Nutrition, International)")


# --- 8. Script Execution ---
if __name__ == "__main__":
    run_newsletter_campaign()