terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_droplet" "mcsi_server" {
  image    = "docker-20-04"
  name     = "mcsi-prod"
  region   = "nyc3"
  size     = "s-2vcpu-4gb"
  ssh_keys = [var.ssh_fingerprint]
}

resource "digitalocean_database_cluster" "mcsi_db" {
  name       = "mcsi-db-cluster"
  engine     = "pg"
  version    = "14"
  size       = "db-s-1vcpu-2gb"
  region     = "nyc3"
  node_count = 1
}

resource "digitalocean_firewall" "mcsi_firewall" {
  name = "mcsi-firewall"

  droplet_ids = [digitalocean_droplet.mcsi_server.id]

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0"]
  }

  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0"]
  }
}