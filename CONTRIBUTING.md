# Contributing to Libro

Hey there! Thanks for your interest in contributing to Libro. This is just a hobby project I work on in my spare time, but I'm totally open to help from others who find it useful or interesting.

## Getting Started

The easiest way to get up and running:

1. Fork the repo
2. Clone your fork locally
3. Make sure you have Python 3.10+ and install `uv` if you don't have it
4. Run `just install` to set up dependencies
5. Run `uv run libro --help` to make sure everything works

## Making Changes

### Development Workflow

- `just lint` - Check your code style (uses ruff)
- `just run <args>` - Test your changes with the CLI
- `just build` - Full build process before submitting

### What I'm Looking For

I'm pretty relaxed about contributions, but here are some things that would be especially welcome:

- **Bug fixes** - If something's broken, I'd love help fixing it
- **Small features** - New commands, import formats, display options, etc.
- **Documentation improvements** - Better help text, examples, etc.
- **Testing** - The project could use more automated tests
- **Performance improvements** - Making things faster is always good

### What Probably Won't Get Merged

- Major architectural changes without discussion first
- Features that significantly complicate the codebase
- Anything that breaks backward compatibility without a really good reason

## Code Style

I use ruff for formatting and linting, so just run `just lint` and fix any issues it finds. The existing code style is pretty straightforward - try to match what's already there.

## Submitting Changes

1. Create a branch for your changes
2. Make your changes and test them
3. Run `just lint` to make sure everything looks good
4. Open a pull request with a clear description of what you changed and why

No need for fancy commit message formats or elaborate PR templates. Just explain what you did in plain English.

## Questions or Ideas?

Feel free to open an issue if you want to discuss something before diving in. I'm usually pretty responsive, though sometimes it might take a few days if I'm busy with other stuff.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (check the LICENSE file).

---

Thanks for considering contributing! Even small improvements are appreciated. 🙂