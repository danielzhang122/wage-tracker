import pygame
import sys
import math
import random
from datetime import datetime, timedelta

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 550
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 197, 94)
DARK_GREEN = (22, 163, 74)
LIGHT_GREEN = (220, 252, 231)
GRAY = (156, 163, 175)
LIGHT_GRAY = (243, 244, 246)
BLUE = (59, 130, 246)
RED = (239, 68, 68)
DARK_RED = (185, 28, 28)

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Real-Time Wage Tracker")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.Font(None, 48)
large_font = pygame.font.Font(None, 64)
medium_font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)
increment_font = pygame.font.Font(None, 36)

class MoneySymbol:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-100, -20)
        self.size = random.randint(25, 45)
        self.speed = random.uniform(1, 3)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-3, 3)
        self.type = random.choice(['dollar', 'coin', 'bill'])
    
    def update(self):
        self.y += self.speed
        self.rotation += self.rotation_speed
        if self.y > HEIGHT + 50:
            self.y = random.randint(-100, -20)
            self.x = random.randint(0, WIDTH)
        return True
    
    def draw(self, surface):
        money_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        if self.type == 'dollar':
            font = pygame.font.Font(None, self.size)
            text = font.render('$', True, (0, 128, 0))
            money_surf.blit(text, (0, 0))
        elif self.type == 'coin':
            pygame.draw.circle(money_surf, (255, 215, 0), (self.size//2, self.size//2), self.size//2)
            pygame.draw.circle(money_surf, (218, 165, 32), (self.size//2, self.size//2), self.size//2, 3)
            font = pygame.font.Font(None, int(self.size * 0.7))
            text = font.render('$', True, (218, 165, 32))
            text_rect = text.get_rect(center=(self.size//2, self.size//2))
            money_surf.blit(text, text_rect)
        else:
            pygame.draw.rect(money_surf, (85, 170, 85), (0, self.size//4, self.size, self.size//2))
            pygame.draw.rect(money_surf, (0, 100, 0), (0, self.size//4, self.size, self.size//2), 2)
            font = pygame.font.Font(None, int(self.size * 0.6))
            text = font.render('$', True, (0, 100, 0))
            text_rect = text.get_rect(center=(self.size//2, self.size//2))
            money_surf.blit(text, text_rect)
        
        rotated = pygame.transform.rotate(money_surf, self.rotation)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated, rect)

class Confetti:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = -10
        self.size = random.randint(4, 10)
        self.color = random.choice([
            (255, 0, 0), (255, 165, 0), (255, 255, 0), 
            (0, 255, 0), (0, 127, 255), (139, 0, 255),
            (255, 20, 147), (0, 255, 255)
        ])
        self.speed = random.uniform(2, 5)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)
    
    def update(self):
        self.y += self.speed
        self.rotation += self.rotation_speed
        return self.y < HEIGHT + 20
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

class FadingIncrement:
    def __init__(self, amount, x, y):
        self.amount = amount
        self.x = x
        self.y = y
        self.alpha = 255
        self.y_offset = 0
        self.duration = 2000
        self.start_time = pygame.time.get_ticks()
    
    def update(self):
        elapsed = pygame.time.get_ticks() - self.start_time
        progress = elapsed / self.duration
        
        if progress >= 1:
            return False
        
        self.alpha = int(255 * (1 - progress))
        self.y_offset = int(30 * progress)
        return True
    
    def draw(self, surface):
        text = f"+${self.amount:.2f}"
        text_surf = increment_font.render(text, True, GREEN)
        text_surf.set_alpha(self.alpha)
        surface.blit(text_surf, (self.x, self.y - self.y_offset))

class FadingMilestone:
    def __init__(self, item_name, x, y):
        self.item_name = item_name
        self.x = x
        self.y = y
        self.alpha = 0
        self.duration = 3000
        self.start_time = pygame.time.get_ticks()
        self.scale = 1.0
    
    def update(self, y_offset=0):
        self.y = 280 + y_offset  # Base position plus offset for stacking
        elapsed = pygame.time.get_ticks() - self.start_time
        progress = elapsed / self.duration
        
        if progress >= 1:
            return False
        
        # Fade in first 15%, hold middle 70%, fade out last 15%
        if progress < 0.15:
            self.alpha = int(255 * (progress / 0.15))
            self.scale = 0.8 + (0.2 * (progress / 0.15))
        elif progress < 0.85:
            self.alpha = 255
            self.scale = 1.0
        else:
            fade_progress = (progress - 0.85) / 0.15
            self.alpha = int(255 * (1 - fade_progress))
            self.scale = 1.0
        
        return True
    
    def draw(self, surface):
        text = f"You've earned {self.item_name}!"
        font_size = int(28 * self.scale)
        font = pygame.font.Font(None, font_size)
        text_surf = font.render(text, True, (255, 215, 0))
        text_surf.set_alpha(self.alpha)
        text_rect = text_surf.get_rect(center=(self.x, self.y))
        
        # Draw background box
        padding = 15
        box_rect = pygame.Rect(
            text_rect.x - padding,
            text_rect.y - padding // 2,
            text_rect.width + padding * 2,
            text_rect.height + padding
        )
        box_surf = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        box_color = (*BLACK, int(200 * (self.alpha / 255)))
        pygame.draw.rect(box_surf, box_color, box_surf.get_rect(), border_radius=8)
        surface.blit(box_surf, (box_rect.x, box_rect.y))
        
        # Draw text
        surface.blit(text_surf, text_rect)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
    
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        text_surf = medium_font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class ToggleButton:
    def __init__(self, x, y, width, height, text_on, text_off):
        self.rect = pygame.Rect(x, y, width, height)
        self.text_on = text_on
        self.text_off = text_off
        self.is_on = False
        self.is_hovered = False
    
    def draw(self, surface):
        color = GREEN if self.is_on else GRAY
        hover_color = DARK_GREEN if self.is_on else (120, 120, 120)
        draw_color = hover_color if self.is_hovered else color
        
        pygame.draw.rect(surface, draw_color, self.rect, border_radius=8)
        text = self.text_on if self.is_on else self.text_off
        text_surf = small_font.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_on = not self.is_on
                return True
        return False

class InputBox:
    def __init__(self, x, y, width, height, label, placeholder=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.placeholder = placeholder
        self.text = ''
        self.active = False
    
    def draw(self, surface):
        label_surf = small_font.render(self.label, True, BLACK)
        surface.blit(label_surf, (self.rect.x, self.rect.y - 30))
        
        color = GREEN if self.active else GRAY
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect, border_radius=8)
        pygame.draw.rect(surface, color, self.rect, 2, border_radius=8)
        
        display_text = self.text if self.text else self.placeholder
        text_color = BLACK if self.text else GRAY
        text_surf = medium_font.render(display_text, True, text_color)
        surface.blit(text_surf, (self.rect.x + 10, self.rect.y + 10))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            else:
                if len(self.text) < 10:
                    self.text += event.unicode

class WageTracker:
    def __init__(self):
        self.hourly_wage = None
        self.tax_rate = 0.25
        self.clock_in_time = None
        self.is_tracking = False
        self.start_time = None
        self.end_time = None
        self.last_update_minute = -1
        self.current_earnings = 0
        self.increments = []
        self.milestone_messages = []
        self.show_summary = False
        self.final_earnings = 0
        self.total_hours = 0
        self.last_milestone = 0
        self.celebration_active = False
        self.celebration_timer = 0
        self.minute_celebration_active = False
        self.minute_celebration_timer = 0
        self.minute_amount = 0
        self.confetti = []
        self.rainbow_offset = 0
        self.money_rain = []
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.unlocked_items = set()
        
        # Milestone items with prices
        self.milestone_items = [
            (5, "a coffee"),
            (10, "a sandwich"),
            (15, "a movie ticket"),
            (25, "a pizza"),
            (50, "a nice dinner"),
            (75, "a new video game"),
            (100, "a pair of shoes"),
            (150, "a smartwatch"),
            (200, "a weekend trip"),
            (300, "a new phone"),
            (500, "a gaming console"),
            (750, "a nice laptop"),
            (1000, "a used car down payment"),
        ]
        
        for _ in range(15):
            self.money_rain.append(MoneySymbol())
        
        self.wage_input = InputBox(150, 150, 300, 50, "Hourly Wage ($)", "15.00")
        self.tax_input = InputBox(150, 250, 300, 50, "Tax Rate (%)", "25")
        self.time_input = InputBox(150, 350, 300, 50, "Clock-In Time (HH:MM)", "09:00")
        self.clock_in_btn = Button(175, 450, 250, 60, "Clock In", GREEN, DARK_GREEN)
        self.clock_out_btn = Button(175, 450, 250, 60, "Clock Out", GREEN, DARK_GREEN)
        self.new_shift_btn = Button(175, 450, 250, 60, "New Shift", BLUE, (37, 99, 235))
        self.tax_toggle = ToggleButton(200, 410, 200, 40, "After Tax", "Before Tax")
    
    def parse_time(self, time_str):
        try:
            hours, minutes = map(int, time_str.split(':'))
            now = datetime.now()
            clock_in = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
            
            if clock_in > now:
                clock_in -= timedelta(days=1)
            
            return clock_in
        except:
            return None
    
    def calculate_earnings(self):
        if not self.start_time or not self.hourly_wage:
            return 0, 0
        
        elapsed = datetime.now() - self.start_time
        total_minutes = int(elapsed.total_seconds() / 60)
        hours = total_minutes / 60
        
        # Calculate earnings based on completed minutes only
        earnings = (total_minutes / 60) * self.hourly_wage
        
        # Check for item milestones
        for price, item_name in self.milestone_items:
            if earnings >= price and price not in self.unlocked_items:
                self.unlocked_items.add(price)
                self.milestone_messages.append(FadingMilestone(item_name, WIDTH // 2, 280))
        
        return earnings, hours
    
    def trigger_minute_celebration(self, amount):
        self.minute_celebration_active = True
        self.minute_celebration_timer = 0
        self.minute_amount = amount
        for _ in range(50):
            self.confetti.append(Confetti())
    
    def get_rainbow_color(self, offset):
        hue = (offset % 360) / 360.0
        h = hue * 6
        c = 1
        x = 1 - abs(h % 2 - 1)
        if h < 1:
            r, g, b = c, x, 0
        elif h < 2:
            r, g, b = x, c, 0
        elif h < 3:
            r, g, b = 0, c, x
        elif h < 4:
            r, g, b = 0, x, c
        elif h < 5:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        return (int(r * 255), int(g * 255), int(b * 255))
    
    def check_minute_update(self):
        if not self.start_time:
            return
        
        elapsed = datetime.now() - self.start_time
        current_minute = int(elapsed.total_seconds() / 60)
        
        if current_minute > self.last_update_minute:
            increment = self.hourly_wage / 60
            self.increments.append(FadingIncrement(increment, WIDTH // 2 - 50, 180))
            self.last_update_minute = current_minute
            # Trigger celebration showing the per-minute earnings
            self.trigger_minute_celebration(increment)
    
    def draw_setup_screen(self):
        screen.fill(LIGHT_GREEN)
        
        title = title_font.render("Wage Tracker", True, BLACK)
        title_rect = title.get_rect(center=(WIDTH // 2, 60))
        screen.blit(title, title_rect)
        
        subtitle = small_font.render("Watch your earnings grow every minute", True, GRAY)
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 100))
        screen.blit(subtitle, subtitle_rect)
        
        self.wage_input.draw(screen)
        self.tax_input.draw(screen)
        self.time_input.draw(screen)
        self.clock_in_btn.draw(screen)
    
    def draw_tracking_screen(self):
        # Handle per-minute celebration
        if self.minute_celebration_active:
            self.minute_celebration_timer += 1
            self.rainbow_offset = (self.rainbow_offset + 5) % 360
            
            intensity = max(0, 15 - self.minute_celebration_timer * 0.1)
            self.shake_offset_x = random.randint(-int(intensity), int(intensity))
            self.shake_offset_y = random.randint(-int(intensity), int(intensity))
            
            if self.minute_celebration_timer > 180:
                self.minute_celebration_active = False
                self.confetti = []
                self.shake_offset_x = 0
                self.shake_offset_y = 0
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0
        
        draw_surface = pygame.Surface((WIDTH, HEIGHT))
        
        if self.minute_celebration_active:
            for i in range(HEIGHT):
                color = self.get_rainbow_color(self.rainbow_offset + i * 0.5)
                pygame.draw.line(draw_surface, color, (0, i), (WIDTH, i))
        else:
            draw_surface.fill(LIGHT_GREEN)
        
        earnings, hours = self.calculate_earnings()
        
        self.check_minute_update()
        
        for money in self.money_rain:
            money.update()
            money.draw(draw_surface)
        
        self.increments = [inc for inc in self.increments if inc.update()]
        
        # Update milestone messages with stacking
        updated_messages = []
        for i, msg in enumerate(self.milestone_messages):
            if msg.update(y_offset=i * 40):  # Stack them 40 pixels apart
                updated_messages.append(msg)
        self.milestone_messages = updated_messages
        
        self.confetti = [c for c in self.confetti if c.update()]
        for c in self.confetti:
            c.draw(draw_surface)
        
        title_color = WHITE if self.minute_celebration_active else BLACK
        display_earnings = earnings * (1 - self.tax_rate) if self.tax_toggle.is_on else earnings
        title_text = "After Tax Earnings" if self.tax_toggle.is_on else "Before Tax Earnings"
        title = medium_font.render(title_text, True, title_color)
        title_rect = title.get_rect(center=(WIDTH // 2, 50))
        draw_surface.blit(title, title_rect)
        
        earnings_text = f"${display_earnings:.2f}"
        earnings_color = WHITE if self.minute_celebration_active else GREEN
        earnings_surf = large_font.render(earnings_text, True, earnings_color)
        earnings_rect = earnings_surf.get_rect(center=(WIDTH // 2, 150))
        
        bg_rect = pygame.Rect(50, 100, WIDTH - 100, 120)
        if self.minute_celebration_active:
            pulse = abs(math.sin(self.minute_celebration_timer * 0.1)) * 10
            bg_rect = pygame.Rect(50 - pulse, 100 - pulse/2, WIDTH - 100 + pulse*2, 120 + pulse)
            border_color = self.get_rainbow_color(self.rainbow_offset + 180)
            pygame.draw.rect(draw_surface, WHITE, bg_rect, border_radius=15)
            pygame.draw.rect(draw_surface, border_color, bg_rect, 5, border_radius=15)
        else:
            pygame.draw.rect(draw_surface, WHITE, bg_rect, border_radius=15)
            pygame.draw.rect(draw_surface, GREEN, bg_rect, 3, border_radius=15)
        
        draw_surface.blit(earnings_surf, earnings_rect)
        
        for inc in self.increments:
            inc.draw(draw_surface)
        
        for msg in self.milestone_messages:
            msg.draw(draw_surface)
        
        if self.minute_celebration_active:
            congrats = title_font.render(f"${self.minute_amount:.2f}!", True, WHITE)
            congrats_rect = congrats.get_rect(center=(WIDTH // 2, 260))
            shadow = title_font.render(f"${self.minute_amount:.2f}!", True, BLACK)
            draw_surface.blit(shadow, (congrats_rect.x + 3, congrats_rect.y + 3))
            draw_surface.blit(congrats, congrats_rect)
        else:
            # Calculate actual elapsed time
            elapsed = datetime.now() - self.start_time
            total_seconds = int(elapsed.total_seconds())
            h = total_seconds // 3600
            m = (total_seconds % 3600) // 60
            s = total_seconds % 60
            time_text = f"Time: {h}h {m}m {s}s"
            time_surf = small_font.render(time_text, True, GRAY)
            time_rect = time_surf.get_rect(center=(WIDTH // 2, 240))
            draw_surface.blit(time_surf, time_rect)
            
            # Show tax deduction info
            if self.tax_toggle.is_on:
                tax_amount = earnings * self.tax_rate
                tax_text = f"(Taxes: -${tax_amount:.2f})"
                tax_surf = small_font.render(tax_text, True, RED)
                tax_rect = tax_surf.get_rect(center=(WIDTH // 2, 265))
                draw_surface.blit(tax_surf, tax_rect)
        
        info_y = 300
        rate_rect = pygame.Rect(50, info_y, 160, 80)
        pygame.draw.rect(draw_surface, LIGHT_GRAY, rate_rect, border_radius=10)
        rate_label = small_font.render("Hourly Rate", True, GRAY)
        rate_value = medium_font.render(f"${self.hourly_wage:.2f}/hr", True, BLACK)
        draw_surface.blit(rate_label, (rate_rect.centerx - rate_label.get_width() // 2, rate_rect.y + 15))
        draw_surface.blit(rate_value, (rate_rect.centerx - rate_value.get_width() // 2, rate_rect.y + 45))
        
        minute_rect = pygame.Rect(230, info_y, 160, 80)
        pygame.draw.rect(draw_surface, LIGHT_GRAY, minute_rect, border_radius=10)
        minute_label = small_font.render("Per Minute", True, GRAY)
        per_minute = self.hourly_wage / 60
        minute_value = medium_font.render(f"${per_minute:.2f}/min", True, BLACK)
        draw_surface.blit(minute_label, (minute_rect.centerx - minute_label.get_width() // 2, minute_rect.y + 15))
        draw_surface.blit(minute_value, (minute_rect.centerx - minute_value.get_width() // 2, minute_rect.y + 45))
        
        time_rect = pygame.Rect(410, info_y, 140, 80)
        pygame.draw.rect(draw_surface, LIGHT_GRAY, time_rect, border_radius=10)
        time_label = small_font.render("Clocked In", True, GRAY)
        time_value = small_font.render(self.start_time.strftime("%I:%M %p"), True, BLACK)
        draw_surface.blit(time_label, (time_rect.centerx - time_label.get_width() // 2, time_rect.y + 15))
        draw_surface.blit(time_value, (time_rect.centerx - time_value.get_width() // 2, time_rect.y + 45))
        
        self.tax_toggle.draw(draw_surface)
        self.clock_out_btn.draw(draw_surface)
        
        screen.fill(BLACK)
        screen.blit(draw_surface, (self.shake_offset_x, self.shake_offset_y))
    
    def draw_summary_screen(self):
        screen.fill(LIGHT_GREEN)
        
        title = title_font.render("Shift Complete!", True, BLACK)
        title_rect = title.get_rect(center=(WIDTH // 2, 50))
        screen.blit(title, title_rect)
        
        earnings_label = small_font.render("Total Earnings (Before Tax)", True, GRAY)
        earnings_label_rect = earnings_label.get_rect(center=(WIDTH // 2, 110))
        screen.blit(earnings_label, earnings_label_rect)
        
        earnings_text = f"${self.final_earnings:.2f}"
        earnings_surf = large_font.render(earnings_text, True, GREEN)
        earnings_rect = earnings_surf.get_rect(center=(WIDTH // 2, 160))
        
        bg_rect = pygame.Rect(50, 130, WIDTH - 100, 80)
        pygame.draw.rect(screen, WHITE, bg_rect, border_radius=15)
        pygame.draw.rect(screen, GREEN, bg_rect, 3, border_radius=15)
        screen.blit(earnings_surf, earnings_rect)
        
        # After tax earnings
        after_tax = self.final_earnings * (1 - self.tax_rate)
        tax_amount = self.final_earnings * self.tax_rate
        
        after_tax_label = small_font.render("After Tax", True, GRAY)
        after_tax_label_rect = after_tax_label.get_rect(center=(WIDTH // 2, 225))
        screen.blit(after_tax_label, after_tax_label_rect)
        
        after_tax_text = f"${after_tax:.2f}"
        after_tax_surf = medium_font.render(after_tax_text, True, DARK_GREEN)
        after_tax_rect = after_tax_surf.get_rect(center=(WIDTH // 2, 255))
        screen.blit(after_tax_surf, after_tax_rect)
        
        tax_text = f"(Tax: -${tax_amount:.2f} at {int(self.tax_rate * 100)}%)"
        tax_surf = small_font.render(tax_text, True, RED)
        tax_rect = tax_surf.get_rect(center=(WIDTH // 2, 280))
        screen.blit(tax_surf, tax_rect)
        
        hours_rect = pygame.Rect(50, 310, 240, 70)
        pygame.draw.rect(screen, WHITE, hours_rect, border_radius=10)
        pygame.draw.rect(screen, GRAY, hours_rect, 2, border_radius=10)
        hours_label = small_font.render("Hours Worked", True, GRAY)
        h = int(self.total_hours)
        m = int((self.total_hours - h) * 60)
        hours_value = medium_font.render(f"{h}h {m}m", True, BLACK)
        screen.blit(hours_label, (hours_rect.centerx - hours_label.get_width() // 2, hours_rect.y + 12))
        screen.blit(hours_value, (hours_rect.centerx - hours_value.get_width() // 2, hours_rect.y + 38))
        
        rate_rect = pygame.Rect(310, 310, 240, 70)
        pygame.draw.rect(screen, WHITE, rate_rect, border_radius=10)
        pygame.draw.rect(screen, GRAY, rate_rect, 2, border_radius=10)
        rate_label = small_font.render("Hourly Rate", True, GRAY)
        rate_value = medium_font.render(f"${self.hourly_wage:.2f}/hr", True, BLACK)
        screen.blit(rate_label, (rate_rect.centerx - rate_label.get_width() // 2, rate_rect.y + 12))
        screen.blit(rate_value, (rate_rect.centerx - rate_value.get_width() // 2, rate_rect.y + 38))
        
        in_rect = pygame.Rect(50, 400, 240, 50)
        pygame.draw.rect(screen, LIGHT_GRAY, in_rect, border_radius=8)
        in_label = small_font.render("Clock In:", True, GRAY)
        in_value = small_font.render(self.start_time.strftime("%I:%M %p"), True, BLACK)
        screen.blit(in_label, (in_rect.x + 15, in_rect.y + 7))
        screen.blit(in_value, (in_rect.x + 15, in_rect.y + 27))
        
        out_rect = pygame.Rect(310, 400, 240, 50)
        pygame.draw.rect(screen, LIGHT_GRAY, out_rect, border_radius=8)
        out_label = small_font.render("Clock Out:", True, GRAY)
        out_value = small_font.render(self.end_time.strftime("%I:%M %p"), True, BLACK)
        screen.blit(out_label, (out_rect.x + 15, out_rect.y + 7))
        screen.blit(out_value, (out_rect.x + 15, out_rect.y + 27))
        
        self.new_shift_btn.draw(screen)
    
    def handle_clock_in(self):
        try:
            wage = float(self.wage_input.text)
            tax_rate = float(self.tax_input.text) / 100
            clock_in = self.parse_time(self.time_input.text)
            
            if wage > 0 and 0 <= tax_rate <= 1 and clock_in:
                self.hourly_wage = wage
                self.tax_rate = tax_rate
                self.start_time = clock_in
                self.is_tracking = True
                self.show_summary = False
                self.last_update_minute = -1
                self.increments = []
                self.last_milestone = 0
                self.celebration_active = False
                self.confetti = []
                self.tax_toggle.is_on = False
                self.unlocked_items = set()
                self.milestone_messages = []
                self.minute_celebration_active = False
                self.minute_celebration_timer = 0
                self.minute_amount = 0
            else:
                print("Invalid input!")
        except ValueError:
            print("Invalid wage or tax rate!")
    
    def handle_clock_out(self):
        self.end_time = datetime.now()
        self.final_earnings, self.total_hours = self.calculate_earnings()
        self.is_tracking = False
        self.show_summary = True
    
    def handle_new_shift(self):
        self.show_summary = False
        self.is_tracking = False
        self.wage_input.text = ''
        self.tax_input.text = ''
        self.time_input.text = ''
        self.start_time = None
        self.end_time = None
        self.final_earnings = 0
        self.total_hours = 0
        self.unlocked_items = set()
        self.milestone_messages = []
        self.last_update_minute = -1
        self.increments = []
        self.last_milestone = 0
        self.celebration_active = False
        self.confetti = []
        self.minute_celebration_active = False
        self.minute_celebration_timer = 0
        self.minute_amount = 0
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.show_summary:
                    if self.new_shift_btn.handle_event(event):
                        self.handle_new_shift()
                elif not self.is_tracking:
                    self.wage_input.handle_event(event)
                    self.tax_input.handle_event(event)
                    self.time_input.handle_event(event)
                    if self.clock_in_btn.handle_event(event):
                        self.handle_clock_in()
                else:
                    self.tax_toggle.handle_event(event)
                    if self.clock_out_btn.handle_event(event):
                        self.handle_clock_out()
            
            if self.show_summary:
                self.draw_summary_screen()
            elif not self.is_tracking:
                self.draw_setup_screen()
            else:
                self.draw_tracking_screen()
            
            pygame.display.flip()
            clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    tracker = WageTracker()
    tracker.run()
