FROM alpine:3.18

# Set working directory
WORKDIR /app

# Copy current directory contents into the image
COPY . /app

# Default command
CMD ["sh"]
