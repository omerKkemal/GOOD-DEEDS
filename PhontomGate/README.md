# PhontomGate – the GUI that lets you pretend you're a real hacker

<p align="center">
  <img src="https://img.shields.io/badge/PHONTOMGATE-FLET%20GUI-10b981?style=for-the-badge&logo=python&logoColor=white&labelColor=1a1a2e" alt="PhontomGate">
</p>

Because apparently not everyone wants to live in a terminal.  
This is the **Flet GUI version** of PhantomGate – for people who like buttons, colors, and clicking things.

---

## What is this?

This is a graphical interface for **PhantomGate** – the agent that talks to SpecterPanel C2.  
It does everything the terminal version does, but with a pretty face.  

You can:
- Control the agent without remembering commands (you're welcome)
- See what's happening with actual visual feedback (wow, so modern)
- Run it on desktop or Android (because why not)
- Pretend you're a real hacker with a GUI (no judgment here)

---

## Running the app

### Desktop (the usual way)

```bash
uv run flet run
```

### Web (because browsers are everywhere)

```bash
uv run flet run --web
```

For more details, check the [Getting Started Guide](https://flet.dev/docs/).  
Or don't. I'm not your boss.

---

## Building the app (for the brave)

Want to share this masterpiece with the world? Build it.

### Android (APK)

```bash
flet build apk -v --cleanup-app --clear-cache
```

Now you have an APK. Go crazy.  
For more details: [Android Packaging Guide](https://flet.dev/docs/publish/android/)

### iOS (IPA)

```bash
flet build ipa -v --cleanup-app --clear-cache
```

Good luck with Apple. You'll need it.  
For more details: [iOS Packaging Guide](https://flet.dev/docs/publish/ios/)

### macOS

```bash
flet build macos -v --cleanup-app --clear-cache
```

Because even Mac users need botnets.  
For more details: [macOS Packaging Guide](https://flet.dev/docs/publish/macos/)

### Linux

```bash
flet build linux -v --cleanup-app --clear-cache
```

For the people who use Linux and want everyone to know.  
For more details: [Linux Packaging Guide](https://flet.dev/docs/publish/linux/)

### Windows

```bash
flet build windows -v --cleanup-app --clear-cache
```

The "just double-click it" experience.  
For more details: [Windows Packaging Guide](https://flet.dev/docs/publish/windows/)

### Web

```bash
flet build web -v --cleanup-app --clear-cache
```

Because who doesn't want a botnet in their browser?  
For more details: [Web Packaging Guide](https://flet.dev/docs/publish/web/)

---

## Related Projects

- **PhantomGate Agent** – [https://github.com/omerKkemal/PhontomGate](https://github.com/omerKkemal/PhontomGate)
- **SpecterPanel C2** – [https://github.com/omerKkemal/oh-tool-v2](https://github.com/omerKkemal/oh-tool-v2)

---

## One more thing...

If you're reading this and you haven't read the PhantomGate warning yet, go do that.  
Seriously. Go. I'll wait.

---

<p align="center">
  <sub>© 2025 PhontomGate – for learning, not for being a jerk. Buttons are fun.</sub>
</p>
