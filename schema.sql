CREATE DATABASE IF NOT EXISTS inventario
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE inventario;

DROP TABLE IF EXISTS movimientos;
DROP TABLE IF EXISTS perfil_modulo;
DROP TABLE IF EXISTS modulos;
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS categorias;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS perfiles;
DROP TABLE IF EXISTS proveedores;

CREATE TABLE perfiles (
  id_perfil INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL UNIQUE,
  descripcion VARCHAR(200) NULL,
  estado TINYINT NOT NULL DEFAULT 1
);

CREATE TABLE usuarios (
  id_usuario INT AUTO_INCREMENT PRIMARY KEY,
  usuario VARCHAR(80) NOT NULL UNIQUE,
  clave VARCHAR(255) NOT NULL,
  nombre VARCHAR(150) NULL,
  correo VARCHAR(150) NULL,
  id_perfil INT NULL,
  estado TINYINT NOT NULL DEFAULT 1,
  FOREIGN KEY (id_perfil) REFERENCES perfiles(id_perfil)
);

CREATE TABLE modulos (
  id_modulo INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  icono VARCHAR(60) NOT NULL,
  ruta VARCHAR(60) NOT NULL,
  orden INT NOT NULL DEFAULT 0,
  estado TINYINT NOT NULL DEFAULT 1
);

CREATE TABLE perfil_modulo (
  id_perfil INT NOT NULL,
  id_modulo INT NOT NULL,
  PRIMARY KEY (id_perfil, id_modulo),
  FOREIGN KEY (id_perfil) REFERENCES perfiles(id_perfil) ON DELETE CASCADE,
  FOREIGN KEY (id_modulo) REFERENCES modulos(id_modulo) ON DELETE CASCADE
);

CREATE TABLE proveedores (
  id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
  nombre_proveedor VARCHAR(200) NOT NULL,
  ruc VARCHAR(11) NULL,
  representante VARCHAR(150) NULL,
  telefono VARCHAR(20) NULL,
  correo VARCHAR(150) NULL,
  direccion VARCHAR(250) NULL,
  estado TINYINT NOT NULL DEFAULT 1,
  fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX (ruc)
);

CREATE TABLE categorias (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL UNIQUE,
  descripcion VARCHAR(200) NULL,
  estado TINYINT NOT NULL DEFAULT 1
);

CREATE TABLE productos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(120) NOT NULL,
  categoria_id INT NOT NULL,
  cantidad INT NOT NULL DEFAULT 0,
  precio DECIMAL(10,2) NOT NULL DEFAULT 0,
  stock_minimo INT NOT NULL DEFAULT 5,
  fecha_vencimiento DATE NULL,
  estado TINYINT NOT NULL DEFAULT 1,
  FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

CREATE TABLE movimientos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  id_producto INT NOT NULL,
  id_proveedor INT NULL,
  tipo_movimiento VARCHAR(20) NOT NULL DEFAULT 'ENTRADA',
  motivo VARCHAR(50) NOT NULL DEFAULT 'COMPRA',
  fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  numero_documento VARCHAR(50) NULL,
  observacion VARCHAR(255) NULL,
  cantidad INT NOT NULL,
  stock_anterior INT NULL DEFAULT 0,
  stock_nuevo INT NULL DEFAULT 0,
  id_usuario INT NULL,
  precio_compra DECIMAL(10,2) NULL,
  subtotal DECIMAL(10,2) NULL,
  FOREIGN KEY (id_producto) REFERENCES productos(id),
  FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor),
  FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);
