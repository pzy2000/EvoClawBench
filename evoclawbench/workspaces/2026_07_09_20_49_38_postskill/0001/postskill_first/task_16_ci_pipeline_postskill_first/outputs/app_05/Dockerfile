FROM ruby:3.2-slim
WORKDIR /app
RUN useradd --create-home --shell /bin/bash appuser
COPY Gemfile Gemfile.lock ./
RUN bundle install
COPY . .
RUN chown -R appuser:appuser /app
USER appuser
EXPOSE 4567
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 CMD ruby -e "require 'net/http'; exit(Net::HTTP.get_response(URI('http://127.0.0.1:4567/health')).code.to_i == 200 ? 0 : 1)"
CMD ["bundle", "exec", "ruby", "app.rb"]
