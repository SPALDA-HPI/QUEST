package peer

import (
	"os"
	"path/filepath"
	"testing"
)

func TestStopIgnoresMissingWireGuardInterface(t *testing.T) {
	directory := t.TempDir()
	ip := filepath.Join(directory, "ip")
	if err := os.WriteFile(ip, []byte("#!/bin/sh\nexit 1\n"), 0o755); err != nil {
		t.Fatal(err)
	}
	t.Setenv("PATH", directory)

	service := &PeeringService{wgInterface: "wg0"}
	if err := service.Stop(); err != nil {
		t.Fatalf("missing cleanup interface should be harmless: %v", err)
	}
}
