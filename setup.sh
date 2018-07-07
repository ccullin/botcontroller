sudo mv *.py /usr/local/src/twitterWebhook
sudo mv requirements.txt /usr/local/src/twitterWebhook
sudo mv twitterWebhook /etc/init.d


sudo chmod 755 /usr/local/src/twitterWebhook/webhook.py
sudo chmod 755 /etc/init.d/twitterWebhook
sudo update-rc.d twitterWebhook defaults

# you can start twitterWebhook with "sudo service twitterWebhook start" ore simply reboot