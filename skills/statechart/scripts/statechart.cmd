@echo off
rem Windows canonical wrapper: direct Node invocation. Requires Node 22.18+/23.6+.
where node >nul 2>nul
if errorlevel 1 (
  echo statechart needs Node 22.18 or later on PATH. 1>&2
  exit /b 127
)
node --disable-warning=ExperimentalWarning "%~dp0statechart.ts" %*
