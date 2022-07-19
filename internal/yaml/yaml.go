package yaml

import (
	"errors"
	"os"

	"gopkg.in/yaml.v2"
)

func ReadYaml(c interface{}, filePath string) error {
	if filePath == "" {
		return errors.New("empty file name")
	}
	f, err := os.Open(filePath)
	if err != nil {
		return err
	}
	defer f.Close()

	err = yaml.NewDecoder(f).Decode(c)
	if err != nil {
		return err
	}
	return nil
}
