# Contributing

Hey! Thanks for taking the time to check out this project. ❤️

If you find a bug, have an idea, or want to help improve the bot, you're welcome to contribute!

Whether you're hosting your own version on Railway, Docker, a VPS, or running it locally, all feedback is appreciated.

## 🐛 Found a Bug?

Something not working as expected? Let me know!

You can report bugs through [GitHub Issues](../../issues/new).

Some examples:

- Video fails to send.
- Cover image isn't applied.
- Caption formatting gets messed up.
- Custom emojis aren't preserved.
- Videos get stuck in the queue.
- Redis connection problems.
- Background worker stops processing jobs.
- Jobs aren't acknowledged or recovered properly.
- Bot doesn't respond.
- Any unexpected errors or crashes.

When opening an issue, please include whatever details you can:

- **What happened?**
- **What did you expect to happen?**
- **How can I reproduce it?**
- **Any error logs or screenshots?**
- **Where are you running the bot?** (Railway, Docker, VPS, or locally.)

If you're hosting your own bot on Railway, please include relevant deployment logs if possible.

Redis or background worker logs can also be helpful when reporting queue-related problems.

Just remember to remove bot tokens, Redis passwords, and other private information before sharing anything.

## 💡 Have an Idea?

Got an idea for a new feature or something that could make the bot better?

Feel free to [open an issue](../../issues/new) and tell me about it.

It doesn't have to be a fully detailed proposal. Just explain your idea and why you think it would be useful.

## 🔧 Want to Contribute Code?

Pull requests are welcome too!

If you want to make changes yourself:

1. Fork this repository.
2. Clone your fork.
3. Create a new branch for your changes.
4. Make your changes.
5. Test them to make sure everything works.
6. Commit your changes.
7. Push your branch to GitHub.
8. Open a pull request against the `main` branch.

For example:

```bash
git checkout -b fix/description-of-fix
```

A few things to keep in mind:

- Keep pull requests focused on one change whenever possible.
- Explain what you changed and why.
- Test your changes before submitting.
- Include any relevant testing details.
- Be careful when changing Redis queue logic or background worker behaviour.

I'll review pull requests before merging. I might ask for changes or suggest improvements along the way. Not every PR will necessarily be merged, but I appreciate the effort!

## ❤️ Thanks!

Whether you report a bug, share an idea, or contribute code, thanks for helping make this project better.

Every bit of feedback helps!