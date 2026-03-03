# 使用 random 提供者（不需要登入任何雲端）
terraform {
  required_providers {
    random = {
      source = "hashicorp/random"
      version = "3.5.1"
    }
  }
}

# 建立一個隨機的寵物名稱（只是字串，不會收費）
resource "random_pet" "my_pet" {
  prefix = "hello"
  length = 2
}

# 輸出結果，讓計畫可以看到
output "pet_name" {
  value = random_pet.my_pet.id
}
