# Використовуємо базовий образ
FROM ubuntu:20.04

# Встановлюємо часовий пояс без запитів
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    tzdata \
    cmake \
    g++ \
    git \
    python3 \
    python3-pip \
    libssl-dev \
    zlib1g-dev \
    libsodium-dev \
    gperf  # Додано для встановлення gperf

# Встановлюємо бажаний часовий пояс (наприклад, UTC)
RUN ln -fs /usr/share/zoneinfo/UTC /etc/localtime && dpkg-reconfigure --frontend noninteractive tzdata

# Завантажуємо TDLib з офіційного репозиторію
RUN git clone https://github.com/tdlib/td.git /tdlib
WORKDIR /tdlib

# Підготовка та збірка TDLib
RUN mkdir -p build && cd build && cmake .. && make

# Копіюємо Python скрипт для взаємодії з Telegram
COPY . /app
WORKDIR /app

# Встановлюємо Python залежності
RUN pip3 install -r requirements.txt

# Запуск програми
CMD ["python3", "bot.py"]
