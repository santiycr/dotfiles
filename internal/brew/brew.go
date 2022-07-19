package brew

import (
	"github.com/rs/zerolog/log"
	"github.com/vrunoa/dotfiles/internal/yaml"
)

type Config struct {
	Formula []string `yaml:"formula"`
}

type brew struct {
	Config Config
}

func (b *brew) InstallFormulas() {
	log.Info().Msg("installing formulas")
}

func New(configFile string) (*brew, error) {
	var config Config
	err := yaml.ReadYaml(&config, configFile)
	if err != nil {
		return nil, err
	}
	return &brew{
		Config: config,
	}, nil
}
