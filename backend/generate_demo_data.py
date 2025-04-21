#!/usr/bin/env python
import os
import django
import random
import datetime
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import models
from accounts.models import User, Wallet, Transaction, Category, Service, Inquiry, InquiryMessage, Review, ReviewComment, BlogCategory, BlogPost, BlogComment
from django.utils import timezone
from django.db import transaction

# Configuration
NUM_CUSTOMERS = 80
NUM_MODERATORS = 10
NUM_BUSINESSES = 40
NUM_SERVICES = 73
NUM_INQUIRIES = 100
NUM_CATEGORIES = 14
NUM_BLOG_CATEGORIES = 8
NUM_BLOG_POSTS = 50
NUM_BLOG_COMMENTS = 120

# Sample data
first_names = ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles',
               'Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen',
               'Emma', 'Olivia', 'Noah', 'Liam', 'Mason', 'Jacob', 'William', 'Ethan', 'Michael', 'Alexander',
               'Ava', 'Sophia', 'Isabella', 'Mia', 'Charlotte', 'Amelia', 'Harper', 'Evelyn', 'Abigail', 'Emily']

last_names = ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor',
              'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Garcia', 'Martinez', 'Robinson',
              'Clark', 'Rodriguez', 'Lewis', 'Lee', 'Walker', 'Hall', 'Allen', 'Young', 'Hernandez', 'King']

domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'icloud.com', 'aol.com', 'protonmail.com']

business_types = ['Consulting', 'Agency', 'Solutions', 'Services', 'Group', 'Partners', 'Associates', 'Enterprises']

category_names = [
    'Legal', 'Finance', 'Lifestyle', 'Technology', 'Health', 'Education', 
    'Home Services', 'Business', 'Marketing', 'Creative', 'Food', 'Travel',
    'Automotive', 'Miscellaneous'
]

category_descriptions = {
    'Legal': 'Legal advice, document preparation, and representation',
    'Finance': 'Financial planning, accounting, and investment services',
    'Lifestyle': 'Personal improvement, fashion, and lifestyle services',
    'Technology': 'IT support, software development, and digital services',
    'Health': 'Wellness, fitness, and healthcare services',
    'Education': 'Tutoring, courses, and educational resources',
    'Home Services': 'Maintenance, repair, and improvement for homes',
    'Business': 'Business consulting, strategy, and operational services',
    'Marketing': 'Promotion, advertising, and brand development',
    'Creative': 'Design, art, and creative professional services',
    'Food': 'Catering, meal preparation, and culinary services',
    'Travel': 'Travel planning, tours, and accommodation services',
    'Automotive': 'Vehicle maintenance, repair, and customization',
    'Miscellaneous': 'Various specialized services'
}

service_descriptions = [
    "Professional {category} services tailored to your specific needs.",
    "Expert {category} solutions with guaranteed satisfaction.",
    "Personalized {category} assistance for individuals and businesses.",
    "Premium {category} services at competitive rates.",
    "Reliable and efficient {category} support whenever you need it.",
    "Innovative {category} approaches to solve your unique challenges.",
    "Trusted {category} expertise with years of experience in the field.",
    "Comprehensive {category} solutions for complex situations.",
    "Specialized {category} services delivered by certified professionals.",
    "Cutting-edge {category} solutions using the latest industry standards."
]

inquiry_subjects = [
    "Question about your {service} services",
    "Inquiry regarding pricing for {service}",
    "Need information about {service}",
    "Requesting details on {service} options",
    "Consultation request for {service}",
    "Interested in your {service} services",
    "Question about availability for {service}",
    "Seeking information about {service} process",
    "Help needed with {service}",
    "Information request for {service} services"
]

inquiry_messages = [
    "Hello, I'm interested in your {service} services. Could you please provide more details about what you offer?",
    "Hi there, I'd like to know more about your {service} pricing. Do you have different packages available?",
    "I'm considering your {service} services for my needs. What is your typical process and timeline?",
    "Can you tell me more about your experience with {service}? I have a specific situation I need help with.",
    "I'm wondering if your {service} services would be a good fit for my requirements. Could we discuss this further?",
    "What sets your {service} apart from others? I'm comparing several options at the moment.",
    "I need your {service} expertise for a project. How soon could you start if we decide to work together?",
    "Do you offer any guarantees or warranties for your {service} services? This is important for my decision.",
    "I have a tight budget for {service}. Do you offer any flexible payment options or discounts?",
    "I've heard good things about your {service} work. Could you share some case studies or examples?"
]

business_responses = [
    "Thank you for your interest in our {service} services. We offer comprehensive solutions tailored to your specific needs.",
    "We appreciate your inquiry about our {service} services. Our pricing starts at $X and varies based on requirements.",
    "Thanks for reaching out about our {service} services. We typically complete projects within Y timeframe.",
    "We have over Z years of experience providing {service} solutions to clients with similar needs.",
    "Our {service} approach is unique because we focus on [specific benefit]. Would you like to schedule a consultation?",
    "What makes our {service} services stand out is our attention to detail and personalized approach.",
    "We could start your {service} project as early as next week. Would you like to discuss specifics?",
    "Yes, we offer a satisfaction guarantee for all our {service} services. Customer satisfaction is our priority.",
    "We understand budget constraints and offer flexible payment plans for our {service} services.",
    "I'd be happy to share some examples of our previous {service} work. We've helped many clients achieve their goals."
]

moderator_messages = [
    "Hello, I'm a moderator assigned to help with your inquiry about {service}. Is there anything specific you'd like clarified?",
    "I'll be moderating this conversation regarding {service}. Please let me know if you need any assistance.",
    "As a moderator, I'm here to ensure your inquiry about {service} gets resolved. How can I help?",
    "I'm stepping in as a moderator for this {service} inquiry. Is there any information I can help provide?",
    "I notice you're inquiring about {service}. As a moderator, I'm here to facilitate this conversation.",
    "I'll be overseeing this discussion about {service}. Please feel free to ask if you have any questions.",
    "As your assigned moderator for this {service} inquiry, I'm here to ensure you get the information you need.",
    "I'm a platform moderator who will be assisting with your {service} inquiry. How can I help today?",
    "I've been assigned as a moderator to help with your {service} request. Is there anything specific you're looking for?",
    "Thank you for your inquiry about {service}. I'm a moderator who will be helping to facilitate this conversation."
]

review_comments = [
    "We appreciate your feedback about our {service} services. We're always working to improve.",
    "Thank you for taking the time to review our {service} work. Your input is valuable to us.",
    "We're glad to hear you had a positive experience with our {service} services.",
    "We're sorry to hear your {service} experience wasn't ideal. We'd love to make it right.",
    "Your review helps us enhance our {service} offerings. Thank you for your honest feedback.",
    "We value your opinion about our {service} work and will take your suggestions into consideration.",
    "Thank you for your review. We're continuously refining our {service} process based on client feedback.",
    "We appreciate your detailed review of our {service} services. It helps potential clients make informed decisions.",
    "Your feedback on our {service} work is important to us. We're committed to excellence in everything we do.",
    "Thank you for your kind words about our {service} services. We look forward to working with you again."
]

moderator_review_comments = [
    "As a platform moderator, I've reviewed this feedback about {service} and find it helpful for other users.",
    "This review provides valuable insight about {service} that can benefit the community.",
    "We appreciate detailed feedback like this about {service} experiences on our platform.",
    "Thank you for sharing your experience with {service}. This helps maintain quality standards.",
    "Your feedback about {service} has been noted by our moderation team. Thank you for contributing.",
    "This review about {service} helps establish transparency and trust within our platform.",
    "We value honest assessments like this about {service} providers on our platform.",
    "As moderators, we appreciate detailed reviews that help others make informed decisions about {service}.",
    "This kind of feedback about {service} is essential for maintaining platform quality standards.",
    "Thank you for taking the time to share your experience with {service}. It benefits the entire community."
]

# Blog data
blog_categories = [
    "Business Tips", "Career Development", "Industry News", "Technology Trends",
    "Customer Success Stories", "How-To Guides", "Service Updates", "Educational Content"
]

blog_titles = [
    "Top 10 {category} Strategies for 2025",
    "The Ultimate Guide to {category} for Beginners",
    "How {category} Can Transform Your Business",
    "5 Common {category} Mistakes to Avoid",
    "The Future of {category}: Trends and Predictions",
    "Understanding {category}: A Comprehensive Overview",
    "Why {category} Matters More Than Ever in Today's Economy",
    "Building Success Through Effective {category}",
    "Mastering {category}: Expert Tips and Tricks",
    "The Evolution of {category} Over the Past Decade"
]

blog_content_templates = [
    """
# {title}

## Introduction
Welcome to our comprehensive guide on {category}. In this article, we'll explore key strategies, best practices, and insights to help you navigate this important area.

## Why {category} Matters
In today's competitive landscape, understanding {category} is essential for success. It allows businesses to:

- Stay ahead of industry trends
- Improve customer satisfaction
- Increase operational efficiency
- Drive sustainable growth

## Key Strategies

### 1. Research and Planning
Before diving into {category}, it's crucial to conduct thorough research and develop a strategic plan. This includes:
- Market analysis
- Competitor assessment
- Goal setting
- Resource allocation

### 2. Implementation
The implementation phase is where your {category} strategy comes to life. Focus on:
- Establishing clear processes
- Training your team
- Setting up monitoring systems
- Creating feedback loops

### 3. Measurement and Optimization
To ensure your {category} efforts are effective, regularly:
- Track key performance indicators
- Gather customer feedback
- Analyze results
- Make data-driven adjustments

## Conclusion
By prioritizing {category} in your business strategy, you'll be well-positioned for long-term success. Remember that this is an ongoing process that requires commitment, flexibility, and continuous learning.
    """,
    
    """
# {title}

## Introduction
{category} has become a critical factor in business success. This article aims to provide you with practical insights and actionable advice to excel in this area.

## Understanding the Fundamentals
At its core, {category} is about creating value through systematic approaches and innovative thinking. The most successful organizations view it as a cornerstone of their operations.

## Best Practices

### Focus on Customer Needs
Always start with your customers' needs and work backward. Ask:
- What problems are they trying to solve?
- How can your offerings address these challenges?
- What unique value can you provide?

### Embrace Technology
Technology continues to transform how businesses approach {category}. Consider:
- Automation tools to improve efficiency
- Data analytics for better decision-making
- Digital platforms to expand reach

### Develop Your Team
Your team is your greatest asset when it comes to {category}. Invest in:
- Regular training and development
- Creating a culture of innovation
- Recognizing and rewarding excellence

## Case Study: Success in Action
[Company X] implemented a comprehensive {category} strategy that resulted in:
- 35% increase in customer satisfaction
- 28% growth in revenue
- 20% reduction in operational costs

## Looking Ahead
The future of {category} lies in adaptability, customer-centricity, and technological integration. Organizations that can effectively balance these elements will thrive in an increasingly competitive marketplace.
    """,
    
    """
# {title}

## Overview
This article explores the essential aspects of {category} and provides practical guidance for implementation in your business.

## The Business Impact of {category}
Effective {category} strategies can significantly impact your bottom line through:

1. **Increased Efficiency**: Streamlining processes and reducing waste
2. **Enhanced Customer Experience**: Meeting and exceeding customer expectations
3. **Competitive Advantage**: Differentiating your business in the marketplace
4. **Innovation Enablement**: Creating an environment that fosters new ideas

## Implementation Framework

### Phase 1: Assessment
Begin by assessing your current approach to {category}:
- Identify strengths and weaknesses
- Benchmark against industry standards
- Determine priority areas for improvement

### Phase 2: Strategy Development
Based on your assessment, develop a comprehensive strategy that includes:
- Clear objectives and key results (OKRs)
- Resource requirements
- Timeline for implementation
- Roles and responsibilities

### Phase 3: Execution
Successfully executing your {category} strategy requires:
- Strong leadership commitment
- Cross-functional collaboration
- Regular communication
- Agile approach to implementation

### Phase 4: Evaluation
Continuously evaluate the effectiveness of your {category} initiatives:
- Establish relevant metrics
- Conduct regular reviews
- Solicit feedback from stakeholders
- Refine approach based on results

## Conclusion
{category} is not a one-time project but an ongoing commitment to excellence. By following this framework and adapting it to your specific context, you can realize significant benefits for your business and your customers.
    """
]

blog_summaries = [
    "Explore the essential strategies and best practices for effective {category} in today's business landscape.",
    "Learn how to leverage {category} to drive growth, improve customer satisfaction, and gain competitive advantage.",
    "Discover the latest trends, insights, and practical tips related to {category} for business success.",
    "A comprehensive guide to understanding and implementing {category} in your organization.",
    "Expert advice on optimizing your approach to {category} for maximum business impact."
]

blog_comments = [
    "Great article! I especially appreciated the insights on {point}.",
    "This was really helpful for understanding {category}. Thanks for sharing!",
    "I've been struggling with {category} and this gave me some practical steps to take.",
    "Do you have any additional resources on {point}? I'd love to learn more.",
    "I implemented some of these strategies and saw immediate improvements in our {category} approach.",
    "Well-written and thorough. I'll be sharing this with my team.",
    "Could you elaborate more on the {point} section? That's particularly relevant to my business.",
    "This article came at the perfect time as we're revamping our {category} strategy.",
    "The case study was particularly illuminating. Great real-world example!",
    "I appreciate the practical framework provided here. Makes {category} seem less overwhelming."
]

comment_points = [
    "performance measurement", "team development", "technology integration",
    "customer feedback loops", "implementation strategies", "market research",
    "resource allocation", "competitive analysis", "strategic planning",
    "process optimization", "change management", "innovation approaches"
]

common_passwords = [
    "password123", "securepass", "userpass2023", "demopassword", 
    "testaccount", "loginpass", "accessme", "letmein2023",
    "userlogin", "safesecure"
]

# User creation functions
def create_user(role, index):
    """Create a user with the specified role"""
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    username = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}"
    email = f"{username}@{random.choice(domains)}"
    
    # Make sure email is unique
    while User.objects.filter(email=email).exists():
        username = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}"
        email = f"{username}@{random.choice(domains)}"
    
    password = random.choice(common_passwords)
    
    # Create the user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=role
    )
    
    # Add a bio based on the role
    if role == User.Role.CUSTOMER:
        user.bio = f"Customer account for testing and demonstration purposes. User #{index}"
    elif role == User.Role.BUSINESS:
        business_name = f"{last_name} {random.choice(business_types)}"
        user.bio = f"Business account: {business_name}. Providing professional services. Business #{index}"
    elif role == User.Role.MODERATOR:
        user.bio = f"Platform moderator responsible for overseeing inquiries and maintaining quality standards. Moderator #{index}"
    
    user.save()
    
    # Add some funds to the wallet
    if hasattr(user, 'wallet'):
        amount = Decimal(str(random.randint(100, 10000)))
        user.wallet.deposit(amount)
    
    return user

def generate_categories():
    """Create service categories"""
    categories = []
    for name in category_names[:NUM_CATEGORIES]:
        category, created = Category.objects.get_or_create(
            name=name,
            defaults={
                'description': category_descriptions.get(name, f"Category for {name} services")
            }
        )
        categories.append(category)
    return categories

def create_service(business_user, categories):
    """Create a service offered by a business"""
    category = random.choice(categories)
    service_name_prefix = random.choice([
        "Premium", "Professional", "Expert", "Elite", "Advanced", 
        "Specialized", "Complete", "Custom", "Essential", "Superior"
    ])
    service_name_suffix = random.choice([
        "Solutions", "Services", "Consulting", "Assistance", "Support",
        "Management", "Guidance", "Planning", "Advisory", "Care"
    ])
    
    service_name = f"{service_name_prefix} {category.name} {service_name_suffix}"
    
    # Make service name unique
    count = 1
    original_name = service_name
    while Service.objects.filter(name=service_name).exists():
        service_name = f"{original_name} {count}"
        count += 1
    
    description = random.choice(service_descriptions).format(category=category.name.lower())
    
    # Set a random fixed price (20% chance of being free, otherwise between 0.50 and 20.00)
    if random.random() < 0.2:
        fixed_price = Decimal('0.00')
    else:
        # Generate a random decimal between 0.50 and 20.00, rounded to 2 decimal places
        fixed_price = Decimal(str(round(random.uniform(0.5, 20.0), 2)))
    
    service = Service.objects.create(
        name=service_name,
        description=description,
        category=category,
        business=business_user,
        fixed_price=fixed_price
    )
    
    return service

def create_inquiry(customer, service, moderators):
    """Create an inquiry about a service"""
    subject = random.choice(inquiry_subjects).format(service=service.name)
    
    # Process fixed price payment if service has a non-zero fixed price
    if service.fixed_price > Decimal('0.00'):
        # Only proceed if customer has enough funds
        if customer.wallet.balance >= service.fixed_price:
            # Create inquiry with transaction to handle the fixed price payment
            with transaction.atomic():
                inquiry = Inquiry.objects.create(
                    service=service,
                    customer=customer,
                    subject=subject
                )
                
                # Process the payment
                customer.wallet.transfer(service.business.wallet, service.fixed_price)
                
                # Add payment message
                InquiryMessage.objects.create(
                    inquiry=inquiry,
                    sender=customer,
                    content=f"Paid {service.fixed_price} to open this inquiry."
                )
        else:
            # Skip creating inquiry if customer can't afford the fixed price
            return None
    else:
        # Free inquiry
        inquiry = Inquiry.objects.create(
            service=service,
            customer=customer,
            subject=subject
        )
    
    # Add customer's initial message
    initial_message = random.choice(inquiry_messages).format(service=service.name.lower())
    InquiryMessage.objects.create(
        inquiry=inquiry,
        sender=customer,
        content=initial_message
    )
    
    # Add business response
    business_response = random.choice(business_responses).format(service=service.name.lower())
    InquiryMessage.objects.create(
        inquiry=inquiry,
        sender=service.business,
        content=business_response
    )
    
    # Sometimes add moderator messages and close the inquiry
    if random.random() < 0.8:  # 80% chance of closed inquiry
        moderator = random.choice(moderators)
        
        # Add moderator message
        mod_message = random.choice(moderator_messages).format(service=service.name.lower())
        InquiryMessage.objects.create(
            inquiry=inquiry,
            sender=moderator,
            content=mod_message
        )
        
        # Add a few more messages from customer and business
        if random.random() < 0.7:  # 70% chance of follow-up messages
            follow_up = "Thank you for the information. I'd like to proceed with your services."
            InquiryMessage.objects.create(
                inquiry=inquiry,
                sender=customer,
                content=follow_up
            )
            
            business_follow_up = "Great! Let's set up a time to discuss the details. Would tomorrow work for you?"
            InquiryMessage.objects.create(
                inquiry=inquiry,
                sender=service.business,
                content=business_follow_up
            )
            
            # Sometimes simulate a transaction between customer and business
            if random.random() < 0.6:  # 60% chance of transaction
                amount = Decimal(str(random.randint(50, 500)))
                
                # Only process transaction if customer has enough funds
                if customer.wallet.balance >= amount:
                    customer.wallet.transfer(service.business.wallet, amount)
                    
                    # Add message about the transaction
                    transaction_message = f"I've sent a payment of ${amount} for your services."
                    InquiryMessage.objects.create(
                        inquiry=inquiry,
                        sender=customer,
                        content=transaction_message
                    )
                    
                    thank_you = "Thank you for your payment! We'll start working on your request immediately."
                    InquiryMessage.objects.create(
                        inquiry=inquiry,
                        sender=service.business,
                        content=thank_you
                    )
        
        # Close the inquiry
        inquiry.close(moderator)
        
        # Sometimes add a review if the inquiry is closed
        if random.random() < 0.7:  # 70% chance of review for closed inquiry
            try:
                rating = random.randint(2, 5)  # Biased toward positive reviews
                comment = f"I had a {rating}/5 experience with this service. " + (
                    "Excellent work and communication!" if rating >= 4 else 
                    "Good service overall with some room for improvement." if rating == 3 else
                    "The service was adequate but not exceptional."
                )
                
                review = Review.objects.create(
                    service=service,
                    user=customer,
                    rating=rating,
                    comment=comment
                )
                
                # Add a business response to the review
                if random.random() < 0.8:  # 80% chance of business response
                    business_comment = random.choice(review_comments).format(service=service.name.lower())
                    ReviewComment.objects.create(
                        review=review,
                        author=service.business,
                        content=business_comment
                    )
                
                # Sometimes add a moderator comment on the review
                if random.random() < 0.3:  # 30% chance of moderator comment
                    mod_comment = random.choice(moderator_review_comments).format(service=service.name.lower())
                    ReviewComment.objects.create(
                        review=review,
                        author=moderator,
                        content=mod_comment
                    )
            except ValueError:
                # If review creation fails (e.g., due to duplicate), just ignore
                pass
    
    return inquiry

def generate_blog_categories():
    """Create blog categories"""
    blog_cats = []
    for name in blog_categories[:NUM_BLOG_CATEGORIES]:
        blog_cat, created = BlogCategory.objects.get_or_create(
            name=name,
            defaults={
                'description': f"Articles and resources about {name.lower()}"
            }
        )
        blog_cats.append(blog_cat)
    return blog_cats


def create_blog_post(author, blog_cats):
    """Create a blog post by a user"""
    category = random.choice(blog_cats)
    title_template = random.choice(blog_titles)
    title = title_template.format(category=category.name)
    
    # Generate slug from title
    from django.utils.text import slugify
    base_slug = slugify(title)
    slug = base_slug
    
    # Ensure slug is unique
    counter = 1
    while BlogPost.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    # Select a content template and format it
    content_template = random.choice(blog_content_templates)
    content = content_template.format(title=title, category=category.name)
    
    # Generate a summary
    summary_template = random.choice(blog_summaries)
    summary = summary_template.format(category=category.name)
    
    # Determine if post is published (90% chance)
    is_published = random.random() < 0.9
    
    # Create the post
    post = BlogPost.objects.create(
        title=title,
        slug=slug,
        content=content,
        summary=summary,
        author=author,
        category=category,
        is_published=is_published,
        views=random.randint(0, 500)  # Random view count
    )
    
    return post


def create_blog_comment(blog_post, author, users):
    """Create a comment on a blog post"""
    # Select a commenter (can be any user except the post author)
    if random.random() < 0.7:  # 70% chance the commenter is not the author
        potential_commenters = [u for u in users if u != author]
        if potential_commenters:
            commenter = random.choice(potential_commenters)
        else:
            commenter = author
    else:
        commenter = author
    
    # Generate comment text
    comment_template = random.choice(blog_comments)
    point = random.choice(comment_points)
    comment_text = comment_template.format(
        point=point, 
        category=blog_post.category.name if blog_post.category else "this topic"
    )
    
    # Create the comment
    comment = BlogComment.objects.create(
        blog_post=blog_post,
        author=commenter,
        content=comment_text
    )
    
    return comment


@transaction.atomic
def generate_demo_data():
    """Generate comprehensive demo data for the application"""
    print("Generating demo data...")
    
    # First, clear all existing data except test users
    print("Clearing existing data...")
    # Keep test users, delete all others
    test_emails = ["admin@test.com", "customer@test.com", "moderator@test.com", "business@test.com"]
    
    # Find test users that already exist
    existing_test_users = User.objects.filter(email__in=test_emails)
    test_user_emails = [user.email for user in existing_test_users]
    
    if existing_test_users.exists():
        print(f"Preserving test users: {', '.join(test_user_emails)}")
        
        # Make sure all test users have wallets with some balance
        for user in existing_test_users:
            if not hasattr(user, 'wallet'):
                from django.apps import apps
                Wallet = apps.get_model('accounts', 'Wallet')
                Wallet.objects.create(user=user, balance=Decimal('100.00'))
            elif user.wallet.balance < Decimal('100.00'):
                user.wallet.balance = Decimal('100.00')
                user.wallet.save()
        
        # Delete all other users
        User.objects.exclude(email__in=test_emails).delete()
    else:
        print("No test users found. Demo data will be generated without preserving any users.")
    
    # Delete all other data
    Transaction.objects.all().delete()
    Wallet.objects.exclude(user__email__in=test_emails).delete()
    Service.objects.all().delete()
    Category.objects.all().delete()
    Inquiry.objects.all().delete()
    InquiryMessage.objects.all().delete()
    Review.objects.all().delete()
    ReviewComment.objects.all().delete()
    BlogPost.objects.all().delete()
    BlogComment.objects.all().delete()
    BlogCategory.objects.all().delete()
    
    print("Existing data cleared. Generating new demo data...")
    
    # Create categories
    categories = generate_categories()
    print(f"Created {len(categories)} categories")
    
    # Create customers
    customers = []
    for i in range(NUM_CUSTOMERS):
        customer = create_user(User.Role.CUSTOMER, i+1)
        customers.append(customer)
    print(f"Created {len(customers)} customers")
    
    # Create moderators
    moderators = []
    for i in range(NUM_MODERATORS):
        moderator = create_user(User.Role.MODERATOR, i+1)
        moderators.append(moderator)
    print(f"Created {len(moderators)} moderators")
    
    # Create businesses
    businesses = []
    for i in range(NUM_BUSINESSES):
        business = create_user(User.Role.BUSINESS, i+1)
        businesses.append(business)
    print(f"Created {len(businesses)} businesses")
    
    # Create services
    services = []
    # Distribute services among businesses
    business_service_counts = {}
    for business in businesses:
        # Each business gets at least one service
        business_service_counts[business.id] = 1
    
    # Distribute remaining services
    remaining_services = NUM_SERVICES - len(businesses)
    for _ in range(remaining_services):
        business_id = random.choice(businesses).id
        business_service_counts[business_id] = business_service_counts.get(business_id, 0) + 1
    
    # Create services for each business
    for business in businesses:
        count = business_service_counts.get(business.id, 1)
        for _ in range(count):
            service = create_service(business, categories)
            services.append(service)
    print(f"Created {len(services)} services")
    
    # Create inquiries
    inquiries = []
    attempts = 0
    max_attempts = NUM_INQUIRIES * 2  # Allow for some failures due to insufficient funds
    
    while len(inquiries) < NUM_INQUIRIES and attempts < max_attempts:
        customer = random.choice(customers)
        service = random.choice(services)
        inquiry = create_inquiry(customer, service, moderators)
        if inquiry:  # Only add if inquiry was successfully created
            inquiries.append(inquiry)
        attempts += 1
        
    print(f"Created {len(inquiries)} inquiries with messages and reviews")
    
    # Generate some random transactions between wallets
    print("Generating additional wallet transactions...")
    num_extra_transactions = 50
    for _ in range(num_extra_transactions):
        from_user = random.choice(customers)
        to_user = random.choice(businesses)
        amount = Decimal(str(random.randint(10, 200)))
        
        if from_user.wallet.balance >= amount:
            try:
                from_user.wallet.transfer(to_user.wallet, amount)
            except ValueError:
                # Skip if transfer fails
                pass
    
    # Generate blog content
    print("Creating blog content...")
    blog_cats = generate_blog_categories()
    print(f"Created {len(blog_cats)} blog categories")
    
    # Create blog posts
    all_users = customers + businesses + moderators
    blog_posts = []
    
    # Distribute blog posts among users (weighted toward businesses and moderators)
    for _ in range(NUM_BLOG_POSTS):
        # Select author with weighting: 50% business, 30% moderator, 20% customer
        author_type = random.choices(
            [User.Role.BUSINESS, User.Role.MODERATOR, User.Role.CUSTOMER],
            weights=[0.5, 0.3, 0.2],
            k=1
        )[0]
        
        if author_type == User.Role.BUSINESS:
            author = random.choice(businesses)
        elif author_type == User.Role.MODERATOR:
            author = random.choice(moderators)
        else:
            author = random.choice(customers)
            
        post = create_blog_post(author, blog_cats)
        blog_posts.append(post)
    
    print(f"Created {len(blog_posts)} blog posts")
    
    # Create blog comments
    blog_comments_list = []
    for post in blog_posts:
        # Each post gets 0-6 comments
        num_comments = random.randint(0, 6)
        for _ in range(num_comments):
            comment = create_blog_comment(post, post.author, all_users)
            blog_comments_list.append(comment)
    
    print(f"Created {len(blog_comments_list)} blog comments")
    
    print("Demo data generation complete!")

if __name__ == "__main__":
    generate_demo_data()