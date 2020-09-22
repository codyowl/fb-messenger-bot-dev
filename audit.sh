#!/bin/bash

code_audit(){
	echo "Sorting libraries"
	isort .
	echo "Formatting code wih black"
	black .
}

code_audit



