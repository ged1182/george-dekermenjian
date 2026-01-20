# Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes and run tests
4. Submit a pull request

## Development Setup

See [README.md](README.md) for setup instructions.

## Code Standards

- **Frontend**: ESLint, TypeScript strict mode
- **Backend**: Ruff, mypy, pytest (90%+ coverage)
- **Commits**: Use conventional commits (feat:, fix:, docs:)

## Running Tests

### Backend

```bash
cd backend
uv sync --dev
uv run pytest
```

### Frontend

```bash
cd web
pnpm lint
pnpm typecheck
pnpm build
```

## Pull Request Checklist

- [ ] Tests pass locally
- [ ] Linting passes
- [ ] Type checking passes
- [ ] Documentation updated if needed
