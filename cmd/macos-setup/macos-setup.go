package main

import (
	"fmt"
	"os"

	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
	"github.com/spf13/cobra"

	"github.com/vrunoa/dotfiles/internal/brew"
	"github.com/vrunoa/dotfiles/internal/version"
)

func setupLogging(verbose bool) {
	zerolog.SetGlobalLevel(zerolog.InfoLevel)
	if verbose {
		zerolog.SetGlobalLevel(zerolog.DebugLevel)
	}
	log.Logger = log.Output(zerolog.ConsoleWriter{Out: os.Stdout, TimeFormat: "15:04:05"})
}

var configFile string

func installCommand() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "install",
		Short: "install",
		Run: func(cmd *cobra.Command, args []string) {
			brew, err := brew.New(configFile)
			if err != nil {
				log.Fatal().Err(err).Msg("failed to setup install")

			}
			brew.InstallFormulas()
		},
	}
	cmd.Flags().StringVarP(&configFile, "config-file", "c", "", "config-file")
	return cmd
}

func main() {
	setupLogging(true)
	mainCmd := &cobra.Command{
		Use:     "macos-setup [command]",
		Short:   "CLI tool for setting up your macOS laptop",
		Version: fmt.Sprintf("%s\n(build %s)", version.Version, version.GitCommit),
	}
	mainCmd.AddCommand(installCommand())
	if err := mainCmd.Execute(); err != nil {
		log.Fatal().Err(err).Msg("wops! seems like we messed up")
		os.Exit(1)
	}
}
