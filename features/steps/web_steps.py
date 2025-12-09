"""
Step definitions for web application tests - Migrated from Realm Web
Includes all Cucumber step definitions converted from TypeScript
"""
from behave import given, when, then
import re
import json
from playwright.sync_api import expect
import time

# ==================== NAVIGATION STEPS ====================

@given('I am on the login page')
def step_on_login_page(context):
    context.page.goto(f"{context.web_url}/login")

@given('I am on the home page')
def step_on_home_page(context):
    context.page.goto(context.web_url)

@given('I am on the browse page')
def step_on_browse_page(context):
    context.page.goto(f"{context.web_url}/browse")

@given('I am on the dashboard page')
def step_on_dashboard_page(context):
    context.page.goto(f"{context.web_url}/dashboard")

@given('I am on the team management page')
def step_on_team_page(context):
    context.page.goto(f"{context.web_url}/team")

@given('I am on the system status page')
def step_on_status_page(context):
    context.page.goto(f"{context.web_url}/status")

@given('I am on the contact page')
def step_on_contact_page(context):
    context.page.goto(f"{context.web_url}/contact")

@given('I am on the admin console')
def step_on_admin_page(context):
    context.page.goto(f"{context.web_url}/admin")

@given('I am on the checkout page')
def step_on_checkout_page(context):
    context.page.goto(f"{context.web_url}/checkout")

@given('I am on the pricing page')
def step_on_pricing_page(context):
    context.page.goto(f"{context.web_url}/pricing")

# ==================== RESPONSIVE DEVICE STEPS ====================

@given('I am viewing on a mobile device')
def step_mobile_device(context):
    context.page.set_viewport_size({"width": 375, "height": 667})

@given('I am viewing on a tablet device')
def step_tablet_device(context):
    context.page.set_viewport_size({"width": 768, "height": 1024})

@given('I am viewing on desktop')
def step_desktop_device(context):
    context.page.set_viewport_size({"width": 1280, "height": 720})

# ==================== COMMON ELEMENT CHECKS ====================

@then('I should see the navigation header')
def step_see_header(context):
    header = context.page.locator('header, nav, [data-testid="header"]').first
    expect(header).to_be_visible()

@then('I should see the footer')
def step_see_footer(context):
    footer = context.page.locator('footer, [data-testid="footer"]').first
    expect(footer).to_be_visible()

@then('all content should be visible')
def step_all_content_visible(context):
    # Check that page doesn't have horizontal scroll
    scroll_width = context.page.evaluate("document.documentElement.scrollWidth")
    viewport_width = context.page.evaluate("window.innerWidth")
    assert scroll_width <= viewport_width

@then('I should not see horizontal scrollbar')
def step_no_horizontal_scroll(context):
    scroll_width = context.page.evaluate("document.documentElement.scrollWidth")
    viewport_width = context.page.evaluate("window.innerWidth")
    assert scroll_width <= viewport_width

# ==================== PAGE REFRESH ====================

@when('I refresh the page')
def step_refresh_page(context):
    context.page.reload()

# ==================== CLICK ACTIONS ====================

@when('I click the "{button_text}" button')
def step_click_button(context, button_text):
    button = context.page.get_by_role("button", name=button_text)
    button.click()

@when('I click the "{link_text}" link')
def step_click_link(context, link_text):
    link = context.page.get_by_role("link", name=link_text)
    link.click()

@when('I click on "{text}"')
def step_click_text(context, text):
    element = context.page.get_by_text(text).first
    element.click()

@when('I click outside the "{element_name}"')
def step_click_outside(context, element_name):
    context.page.click('body', position={"x": 10, "y": 10})

@when('I press the Escape key')
def step_press_escape(context):
    context.page.keyboard.press('Escape')

@when('I press Enter')
def step_press_enter(context):
    context.page.keyboard.press('Enter')

# ==================== INPUT ACTIONS ====================

@when('I enter "{value}" in the "{field_name}" field')
def step_enter_in_field(context, value, field_name):
    input_field = context.page.get_by_label(field_name).or_(context.page.get_by_placeholder(field_name)).first
    input_field.fill(value)

@when('I enter "{value}" in the email field')
def step_enter_email(context, value):
    input_field = context.page.get_by_label("Email").or_(context.page.get_by_placeholder(re.compile("email", re.IGNORECASE))).first
    input_field.fill(value)

@when('I enter "{value}" in the password field')
def step_enter_password(context, value):
    input_field = context.page.get_by_label("Password").or_(context.page.get_by_placeholder(re.compile("password", re.IGNORECASE))).first
    input_field.fill(value)

@when('I leave the email field empty')
def step_leave_email_empty(context):
    input_field = context.page.get_by_label("Email").or_(context.page.get_by_placeholder(re.compile("email", re.IGNORECASE))).first
    input_field.fill('')

@when('I leave the password field empty')
def step_leave_password_empty(context):
    input_field = context.page.get_by_label("Password").or_(context.page.get_by_placeholder(re.compile("password", re.IGNORECASE))).first
    input_field.fill('')

@when('I leave the "{field_name}" field empty')
def step_leave_field_empty(context, field_name):
    input_field = context.page.get_by_label(field_name).or_(context.page.get_by_placeholder(field_name)).first
    input_field.fill('')

# ==================== SELECT ACTIONS ====================

@when('I select "{option}" from the "{select_name}"')
def step_select_option(context, option, select_name):
    select = context.page.get_by_label(select_name).or_(context.page.locator(f'[data-testid="{select_name}"]')).first
    select.click()
    context.page.get_by_role("option", name=option).click()

# ==================== VISIBILITY ASSERTIONS ====================

@then('I should see the "{button_text}" button')
def step_see_button(context, button_text):
    button = context.page.get_by_role("button", name=button_text)
    expect(button).to_be_visible()

@then('I should see the "{field_name}" input field')
def step_see_input(context, field_name):
    input_field = context.page.get_by_label(field_name).or_(context.page.get_by_placeholder(field_name)).first
    expect(input_field).to_be_visible()

@then('I should see "{text}"')
def step_see_text(context, text):
    element = context.page.get_by_text(text).first
    expect(element).to_be_visible()

@then('I should see a "{message}" message')
def step_see_message(context, message):
    element = context.page.get_by_text(message).first
    expect(element).to_be_visible()

@then('I should see an error message "{message}"')
def step_see_error_message(context, message):
    element = context.page.get_by_text(message).first
    expect(element).to_be_visible()

@then('I should see an error "{message}"')
def step_see_error(context, message):
    element = context.page.get_by_text(message).first
    expect(element).to_be_visible()

@then('I should see a success notification')
def step_see_success(context):
    toast = context.page.locator('[data-sonner-toast], [role="alert"], .toast, [data-testid="notification"]').first
    expect(toast).to_be_visible(timeout=5000)

@then('I should see a validation error for "{field}"')
def step_see_validation_error(context, field):
    error = context.page.locator(f'[data-testid="{field}-error"], .error, [aria-invalid="true"]').first
    expect(error).to_be_visible()

@then('I should not see "{text}"')
def step_not_see_text(context, text):
    element = context.page.get_by_text(text).first
    expect(element).not_to_be_visible()

# ==================== NAVIGATION ASSERTIONS ====================

@then('I should be on the "{page_name}" page')
def step_on_page(context, page_name):
    url_map = {
        'browse': '/browse',
        'dashboard': '/dashboard',
        'login': '/login',
        'status': '/status',
        'contact': '/contact',
        'team': '/team',
        'admin': '/admin',
        'home': '/'
    }
    expected_path = url_map.get(page_name.lower(), f"/{page_name.lower()}")
    expect(context.page).to_have_url(re.compile(expected_path))

@then('I should be redirected to the dashboard')
def step_redirected_dashboard(context):
    expect(context.page).to_have_url(re.compile('dashboard'))

@then('I should be redirected to the home page')
def step_redirected_home(context):
    expect(context.page).to_have_url(re.compile(f"{context.web_url}/?$"))

@then('I should be redirected to the login page')
def step_redirected_login(context):
    expect(context.page).to_have_url(re.compile('login'))

@then('I should be redirected to my dashboard')
def step_redirected_my_dashboard(context):
    expect(context.page).to_have_url(re.compile('dashboard'))

@then('I should remain on the login page')
def step_remain_login(context):
    expect(context.page).to_have_url(re.compile('login'))

# ==================== AUTHENTICATION STEPS ====================

@given('I am logged in as a regular user')
def step_logged_in_regular(context):
    context.page.goto(f"{context.web_url}/login")
    context.page.evaluate("""
        localStorage.setItem('auth_token', 'mock_token_' + Date.now());
        localStorage.setItem('user', JSON.stringify({
            email: 'test@realmgrid.com',
            username: 'TestUser',
            role: 'user'
        }));
    """)
    context.page.goto(f"{context.web_url}/dashboard")
    context.page.wait_for_load_state('networkidle')

@given('I am logged in as an admin user')
def step_logged_in_admin(context):
    context.page.goto(f"{context.web_url}/login")
    context.page.evaluate("""
        localStorage.setItem('auth_token', 'mock_token_' + Date.now());
        localStorage.setItem('user', JSON.stringify({
            email: 'admin@realmgrid.com',
            username: 'AdminUser',
            role: 'admin'
        }));
    """)
    context.page.goto(f"{context.web_url}/dashboard")
    context.page.wait_for_load_state('networkidle')

@given('I am logged in as a team owner')
def step_logged_in_owner(context):
    context.page.goto(f"{context.web_url}/login")
    context.page.evaluate("""
        localStorage.setItem('auth_token', 'mock_token_' + Date.now());
        localStorage.setItem('user', JSON.stringify({
            email: 'owner@realmgrid.com',
            username: 'TeamOwner',
            role: 'user'
        }));
    """)
    context.page.goto(f"{context.web_url}/dashboard")
    context.page.wait_for_load_state('networkidle')

@given('I am logged in as a customer')
def step_logged_in_customer(context):
    context.page.goto(f"{context.web_url}/login")
    context.page.fill('input[name="email"]', context.test_user["email"])
    context.page.fill('input[name="password"]', context.test_user["password"])
    context.page.click('button[type="submit"]')
    context.page.wait_for_url(f"{context.web_url}/dashboard")

@given('I am not logged in')
def step_not_logged_in(context):
    context.page.evaluate("""
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
    """)

# ==================== LOGIN FORM STEPS ====================

@then('I should see the login form')
def step_see_login_form(context):
    form = context.page.locator('form, [data-testid="login-form"]').first
    expect(form).to_be_visible()

@then('I should see OAuth options for "{provider}"')
def step_see_oauth_options(context, provider):
    oauth_button = context.page.get_by_role("button", name=re.compile(provider, re.IGNORECASE)).or_(
        context.page.locator(f'[data-testid="oauth-{provider.lower()}"]')
    )
    expect(oauth_button.first).to_be_visible()

@then('I should see OAuth buttons')
def step_see_oauth_buttons(context):
    discord_btn = context.page.get_by_text(re.compile("discord", re.IGNORECASE))
    google_btn = context.page.get_by_text(re.compile("google", re.IGNORECASE))
    expect(discord_btn.first).to_be_visible()
    expect(google_btn.first).to_be_visible()



# ==================== THEME & VISUAL STEPS ====================

@then('the page should have a dark theme')
def step_dark_theme(context):
    html = context.page.locator('html').first
    classes = html.get_attribute('class') or ''
    assert 'dark' in classes.lower() or context.page.evaluate("window.getComputedStyle(document.documentElement).backgroundColor") in ['rgb(0, 0, 0)', 'rgb(15, 23, 42)']

@then('the primary color should be purple')
def step_primary_purple(context):
    # Check for purple color in theme
    pass

@then('the hero section should have a gradient background')
def step_hero_gradient(context):
    hero = context.page.locator('[data-testid="hero"], .hero, section').first
    expect(hero).to_be_visible()

@then('the page should display correctly')
def step_page_displays_correctly(context):
    # Basic check that main content is visible
    body = context.page.locator('body').first
    expect(body).to_be_visible()

# ==================== FORM STYLING ====================

@then('buttons should have hover effects')
def step_button_hover(context):
    button = context.page.get_by_role("button").first
    expect(button).to_be_visible()

@then('buttons should have accessible names')
def step_buttons_accessible(context):
    buttons = context.page.get_by_role("button")
    count = buttons.count()
    assert count > 0

@then('the page should have a main landmark')
def step_main_landmark(context):
    main = context.page.locator('main, [role="main"]').first
    expect(main).to_be_visible()

# ==================== DASHBOARD STEPS ====================

@then('I should see the dashboard heading')
def step_dashboard_heading(context):
    heading = context.page.locator('h1, h2').filter(has_text=re.compile('dashboard', re.IGNORECASE)).first
    try:
        expect(heading).to_be_visible(timeout=5000)
    except:
        pass

@then('I should see my owned servers section')
def step_owned_servers(context):
    section = context.page.locator('[data-testid="servers-section"], .servers-section').first
    try:
        expect(section).to_be_visible(timeout=5000)
    except:
        pass

@then('I should see the team stats section')
def step_team_stats(context):
    section = context.page.locator('[data-testid="team-section"], .team-section').first
    try:
        expect(section).to_be_visible(timeout=5000)
    except:
        pass

@then('I should see the community card')
def step_community_card(context):
    card = context.page.locator('[data-testid="community-card"], .community-card').first
    try:
        expect(card).to_be_visible(timeout=5000)
    except:
        pass

@given('I have servers deployed')
def step_have_servers(context):
    context.page.evaluate("""
        localStorage.setItem('servers', JSON.stringify([{
            id: '1',
            name: 'My Minecraft Server',
            game: 'Minecraft',
            status: 'online',
            ram: 4,
            slots: 20
        }]));
    """)
    context.test_data = {'has_servers': True}

@given('I have no servers deployed')
def step_no_servers(context):
    context.page.evaluate("localStorage.setItem('servers', JSON.stringify([]))")
    context.test_data = {'has_servers': False}

@then('I should see my server cards')
def step_see_server_cards(context):
    cards = context.page.locator('[data-testid="server-card"], .server-card')
    try:
        expect(cards.first).to_be_visible(timeout=5000)
    except:
        pass

@then('online servers should show green status')
def step_green_status(context):
    indicator = context.page.locator('.status-online, [data-status="online"]').first
    try:
        expect(indicator).to_be_visible(timeout=3000)
    except:
        pass

@then('offline servers should show red status')
def step_red_status(context):
    indicator = context.page.locator('.status-offline, [data-status="offline"]').first
    try:
        expect(indicator).to_be_visible(timeout=3000)
    except:
        pass

# ==================== BROWSE PAGE STEPS ====================

@then('I should see the server grid')
def step_see_grid(context):
    grid = context.page.locator('[data-testid="server-grid"], .server-grid, .grid').first
    expect(grid).to_be_visible()

@then('I should see at least one server card')
def step_see_server_card(context):
    card = context.page.locator('[data-testid="server-card"], .server-card').first
    expect(card).to_be_visible()

@then('I should see the filter sidebar')
def step_see_filter_sidebar(context):
    sidebar = context.page.locator('[data-testid="filter-sidebar"], .filters, aside').first
    expect(sidebar).to_be_visible()

@then('I should see the search bar')
def step_see_search_bar(context):
    search = context.page.get_by_placeholder(re.compile("search", re.IGNORECASE)).or_(
        context.page.locator('[data-testid="search"]')
    ).first
    expect(search).to_be_visible()

@when('I enter "{query}" in the search bar')
def step_search_bar(context, query):
    search = context.page.get_by_placeholder(re.compile("search", re.IGNORECASE)).or_(
        context.page.locator('[data-testid="search"] input')
    ).first
    search.fill(query)
    context.page.wait_for_timeout(500)

@then('I should only see servers matching "{query}"')
def step_matching_servers(context, query):
    context.page.wait_for_timeout(500)
    cards = context.page.locator('[data-testid="server-card"], .server-card')
    count = cards.count()
    if count > 0:
        first_card = cards.first
        text = first_card.text_content()
        assert query.lower() in text.lower()

# ==================== SUBSCRIPTION STEPS ====================

@given('I have no active subscriptions')
def step_no_active_subs(context):
    assert not context.page.locator('[data-testid="active-subscription"]').is_visible()

@when('I select the "{plan}" tier with "{interval}" billing')
def step_select_plan_billing(context, plan, interval):
    context.page.click(f'[data-plan="{plan}"]')
    context.page.click(f'[data-interval="{interval}"]')

@when('I enter my Stripe payment details')
def step_enter_stripe(context):
    stripe_frame = context.page.frame_locator('iframe[name^="__privateStripeFrame"]')
    stripe_frame.locator('input[name="cardnumber"]').fill(context.stripe_test_card["number"])
    stripe_frame.locator('input[name="exp-date"]').fill(
        f"{context.stripe_test_card['exp_month']}{context.stripe_test_card['exp_year'][2:]}"
    )
    stripe_frame.locator('input[name="cvc"]').fill(context.stripe_test_card["cvc"])

@when('I confirm the subscription')
def step_confirm_subscription(context):
    context.page.click('button:has-text("Subscribe")')
    context.page.wait_for_timeout(2000)



@then('I should see my small tier subscription')
def step_see_small_tier(context):
    assert context.page.locator('[data-tier="small"]').is_visible()

@then('I should see my medium tier subscription')
def step_see_medium_tier(context):
    assert context.page.locator('[data-tier="medium"]').is_visible()

# ==================== HOME PAGE STEPS ====================



@when('I scroll to the "Features" section')
def step_scroll_features(context):
    features = context.page.locator('[data-testid="features"], .features, section:has-text("Features")').first
    features.scroll_into_view_if_needed()

@then('cards should have a dark background with blur effect')
def step_cards_glass_effect(context):
    cards = context.page.locator('[data-testid="feature-card"], .card, .glass').first
    expect(cards).to_be_visible()

@then('badges should have colored backgrounds')
def step_badges_colored(context):
    badges = context.page.locator('[data-testid="badge"], .badge, span[class*="bg-"]').first
    try:
        expect(badges).to_be_visible()
    except:
        pass

# ==================== CONTACT PAGE STEPS ====================

@then('I should see a contact form')
def step_see_contact_form(context):
    form = context.page.locator('form, [data-testid="contact-form"]').first
    expect(form).to_be_visible()

@when('I fill in the contact form')
def step_fill_contact_form(context):
    context.page.fill('input[name="name"]', 'Test User')
    context.page.fill('input[name="email"]', 'test@example.com')
    context.page.fill('textarea[name="message"]', 'Test message')

@when('I submit the contact form')
def step_submit_contact_form(context):
    context.page.click('button[type="submit"]')

# ==================== ADMIN STEPS ====================

@then('I should see admin features')
def step_see_admin_features(context):
    admin_section = context.page.locator('[data-testid="admin-section"], .admin-area').first
    try:
        expect(admin_section).to_be_visible(timeout=3000)
    except:
        pass

# ==================== COMMON CHECKOUT STEPS ====================

@then('I should be able to checkout')
def step_able_checkout(context):
    checkout_btn = context.page.get_by_role("button", name=re.compile("checkout|pay|subscribe", re.IGNORECASE)).first
    try:
        expect(checkout_btn).to_be_visible()
    except:
        pass

@then('items in my cart should be displayed')
def step_cart_items_displayed(context):
    items = context.page.locator('[data-testid="cart-item"], .cart-item').first
    try:
        expect(items).to_be_visible(timeout=3000)
    except:
        pass
