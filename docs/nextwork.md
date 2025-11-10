## EC2 firewall (Ubuntu’s ufw
- Check if ufw (firewall) is blocking access:
```bash
sudo ufw status
```

- If it’s active and port 80 isn’t allowed:
```bash
sudo ufw allow 80/tcp
sudo ufw reload
```
