# Use slim python image
FROM python:3.12-slim

# Install needed libraries
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    --no-install-recommends

# Add Chrome GPG Key
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-linux-signing-keyring.gpg

# Add Chrome repository
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Install Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable

# Install ChromeDriver
RUN CHROME_VERSION=$(google-chrome-stable --version | awk '{print $3}' | cut -d '.' -f 1) && \
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROME_VERSION}.0/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver

# Create working directory
WORKDIR /app

# Copy all project files
COPY . .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Start Flask App
CMD ["python", "flask_search_judgments.py"]
