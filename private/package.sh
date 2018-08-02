#!/bin/bash

# ---------------------------------------------------------------------------
# File:    package.sh
# Author:  Brigitte Bigi
# Date:    October, 2014
# Brief:   SPPAS packaging script.
# ---------------------------------------------------------------------------
#
# This script can perform 4 actions:
#
#  1. Diagnosis
#
#    a/ Compare SPPAS automatic annotation results to a reference.
#    b/ Execute all Unittests of the API
#
#  2. Manual and documentation
#
#    a/ Use sphinx to generate the API reference manual.
#       It results a "api" folder in the web directory.
#    b/ Use pandoc to generate the User documentation (html and PDF),
#       from markdown files.
#
#  3. Package
#
#    Create a zip file with the public part of SPPAS.
#
#  4. Clean
#
# ---------------------------------------------------------------------------
#
#  After packaging, I have just to (manually) update my webpage:
#    - edit/update the download.html page
#    - copy the zip file on the server: http://www.sppas.org/
#    - replace the content of the server by the "web" directory of this package.
#
# ---------------------------------------------------------------------------


# ===========================================================================
# Fix global variables
# ===========================================================================

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Program to package
PROGRAM_DIR=$(dirname $HERE)

PROGRAM_NAME="SPPAS"
PROGRAM_AUTHOR="Brigitte Bigi"
PROGRAM_VERSION=$(grep -e "__version__=" $PROGRAM_DIR/sppas/src/config/sglobal.py | awk -F'=' '{print $2}' | cut -f2 -d'"')

# Files and directories to be used
BIN_DIR="bin"
TEMP="/tmp/sppas_package.txt"

# Actions to perform in this script
DO_DIAGNOSIS="False"
DO_MANUAL="False"
DO_PACKAGE="False"
DO_TUTO="False"
DO_CLEAN="False"

# User-Interface
MSG_HEADER="SPPAS $PROGRAM_VERSION, a program written by Brigitte Bigi."
TODAY=$(date "+%Y-%m-%d")

BLACK='\e[0;30m'
WHITE='\e[1;37m'
LIGHT_GRAY='\e[0;37m'
DARK_GRAY='\e[1;30m'
BLUE='\e[0;34m'
DARK_BLUE='\e[1;34m'
GREEN='\e[0;32m'
LIGHT_GREEN='\e[1;32m'
CYAN='\e[0;36m'
LIGHT_CYAN='\e[1;36m'
RED='\e[0;31m'
LIGHT_RED='\e[1;31m'
PURPLE='\e[0;35m'
LIGHT_PURPLE='\e[1;35m'
BROWN='\e[0;33m'
YELLOW='\e[1;33m'
NC='\e[0m' # No Color


# ===========================================================================
# Functions generic
# ===========================================================================


# Print a title message on stdout
# Parameters:
#  $1: message to print
function fct_echo_title {
    echo -e "${LIGHT_GREEN}-----------------------------------------------------------------------"
    echo -e "${BROWN}$1"
    echo -e "${LIGHT_GREEN}-----------------------------------------------------------------------${NC}"
}


# Print the header message on stdout
function fct_echo_header {
    echo
    echo -e "${LIGHT_GREEN}-----------------------------------------------------------------------"
    echo -e "${LIGHT_RED}$MSG_HEADER"
    echo -e "${LIGHT_GREEN}-----------------------------------------------------------------------${NC}"
    echo
}


# Print an error message, then exit
# Parameters:
#   $1: error message
function fct_exit_error {
    fct_echo_header
    echo -e "${RED}Error: $1${NC}"
    echo
    exit 1
}


# Is a program currently running? Stop this script if yes.
# Exclude this script PID in case this function is applied to this script!
# Parameter:
#  $1: program name
function fct_test_running {
    isrun=`ps ax | grep -v "$BASHPID" | awk '{print $5}' | grep -c "$1"`
    if [ $isrun -gt 1 ]; then
        fct_exit_error "Another instance of the program $1 is running. It must be stopped before using it again."
    fi
}


# ===========================================================================
# Functions to clean
# ===========================================================================


# Clean the current directory: remove temporary files
function fct_clean_temp {
    if [ -e $TEMP ];  then rm $TEMP;  fi

    rm bin/*/*.pyc &> /dev/null
    rm bin/*/*.dump &> /dev/null

}


# Remove SPPAS annotations of the test directory
function fct_clean_test {
    rm $SAMPLES_DIR/sample2.*     &> /dev/null
    rm $SAMPLES_DIR/*.log         &> /dev/null
    rm $SAMPLES_DIR/test_xra.xra       &> /dev/null
    rm $SAMPLES_DIR/gaps.TextGrid      &> /dev/null
    rm $SAMPLES_DIR/oriana1-*.TextGrid &> /dev/null
    rm $SAMPLES_DIR/sample.xra         &> /dev/null
    rm $SAMPLES_DIR/sample3.mrk        &> /dev/null
    rm $SAMPLES_DIR/sampleascii.csv    &> /dev/null
}


# Clean the SPPAS package
function fct_clean_sppas {
    rm  -r $PROGRAM_DIR/samples/*/*-token*          &> /dev/null
    rm  -r $PROGRAM_DIR/samples/*/*-phon*           &> /dev/null
    rm  -r $PROGRAM_DIR/samples/*/*-palign*         &> /dev/null
    rm  -r $PROGRAM_DIR/samples/*/*-salign*         &> /dev/null
    rm  -r $PROGRAM_DIR/samples/*/*-ralign*         &> /dev/null
    rm  -r $PROGRAM_DIR/samples/*/*-momel*          &> /dev/null
    rm  -r $PROGRAM_DIR/samples/*/*-merge*          &> /dev/null
    rm  -r $PROGRAM_DIR/samples/*/*log              &> /dev/null
    rm  -r $PROGRAM_DIR/samples/*/*.list            &> /dev/null
    rm  -r $PROGRAM_DIR/samples/*/*.momel.*         &> /dev/null
    rm  -r $PROGRAM_DIR/samples/*/*.momel           &> /dev/null
    rm  -r $PROGRAM_DIR/samples/*/*-ipu.TextGrid    &> /dev/null
    rm  -r $PROGRAM_DIR/samples/*.log               &> /dev/null
    rm  -r $PROGRAM_DIR/samples/*/*.xra               &> /dev/null
    rm $PROGRAM_DIR/sppas/*/*.pyc                   &> /dev/null
    rm $PROGRAM_DIR/sppas/*/*/*.pyc                 &> /dev/null
    rm $PROGRAM_DIR/sppas/*/*/*/*.pyc               &> /dev/null
    rm $PROGRAM_DIR/sppas/*/*/*/*/*.pyc             &> /dev/null
    rm $PROGRAM_DIR/resources/dict/*.dump           &> /dev/null
    rm $PROGRAM_DIR/resources/vocab/*.dump          &> /dev/null
    rm $PROGRAM_DIR/documentation/solutions/*.pyc   &> /dev/null
    rm $PROGRAM_DIR/sppas/etc/settings.dump
}


# ===========================================================================
# Functions to extract the command-line
# ===========================================================================


# Print the Usage message on stdout
function fct_echo_usage {
    fct_echo_header
    echo -e "${CYAN}Usage: $0 [options]${NC}"
    echo
    echo -e "where options are:${LIGHT_CYAN}"
    echo -e "    -p|--package     package"
    echo -e "    -d|--diagnosis   diagnosis"
    echo -e "    -t|--tutorials   tutorials for the web"
    echo -e "    -m|--manual      API manual with sphinx"
    echo -e "    -c|--clean       clean (remove all un-necessary files)"
    echo -e "    -a|--all         (package+diagnosis+tutorials+clean)"
    echo -e "    -h|--help        print this help${NC}"
    echo
}

# Test if this scripts has the expected number of arguments
# Parameters:
#   $1: nb args
function fct_test_nb_args {
    local maxargs=7
    local minargs=1
    # The command is given without args: print usage
    if [ "$1" -eq 0 ]
    then
        echo -e "${DARK_BLUE}Help.${NC}"
        fct_echo_usage
        exit 0
    fi
    # Too many args: print error and usage
    if [ "$1" -gt $maxargs ]
    then
        echo -e "${DARK_BLUE}Too many arguments.${NC}"
        fct_echo_usage
        exit 1
    fi
    # Too few args: print error and usage
    if [ "$1" -lt $minargs ]
    then
        echo -e "${DARK_BLUE}Too few arguments.${NC}"
        fct_echo_usage
        exit 1
    fi
}


# Fix options from args
# Parameters:
#   $1: all the arguments
function fct_get_args {

    for arg in $@; do
        case $arg in
            -h|--help)
                fct_echo_usage
                exit 0
                ;;
            -c|--clean)
                DO_CLEAN="True";
                ;;
            -a|--all)
                DO_PACKAGE="True";
                DO_DIAGNOSIS="True";
                DO_MANUAL="True";
                DO_TUTO="True";
                DO_CLEAN="True";
                ;;
            -p|--package)
                DO_PACKAGE="True";
                ;;
            -d|--diagnosis)
                DO_DIAGNOSIS="True";
                ;;
            -m|--manual)
                DO_MANUAL="True";
                ;;
            -t|--tutorials)
                DO_TUTO="True";
                ;;
            *)
                #unknown option
                echo -e "${DARK_BLUE}Unregognized option $1.${NC}"
                fct_echo_usage
                exit 1
            ;;
        esac
        done
}


# ===========================================================================
# Functions for the DIAGNOSIS
# ===========================================================================


# Test automatic annotations in the "bin" directory of SPPAS
function fct_test_annotations {
    echo -e "${BROWN} - Test of the annotation scripts.${NC}"
    echo >> $_annotations
    echo "##########  ${PROGRAM_NAME} Annotations diagnosis - $TODAY #########" >> diagnosis.log
    echo >> diagnosis.log

    $BIN_DIR/test_annotations.sh -a > $TEMP

    local error=`grep -c 'error' $TEMP`
    if [ $error -eq 0 ]; then
         echo " ... Test: Success"
    else
         echo " ... Test: $error error(s)."
    fi

    cat $TEMP >> diagnosis.log
    echo >> diagnosis.log
    echo " ######### ############################ ######### " >> diagnosis.log
    echo >> diagnosis.log

    rm $TEMP
}

# Exec python unittest on a package.
function fct_perform_unittest {
    # for help:
    # python -m unittest -h
    # Here, we use:
    # -v for verbosity
    # -t top-level-project for successfull imports
    # automatically discover tests with pattern "test*.py" from -s start-directory
    touch $TEMP
    echo " ... Test $1 "

    echo >> $TEMP
    echo " ================================================ " >> $TEMP
    echo " Start test of $1 " >>  $TEMP
    python -m unittest discover -s "$PROGRAM_DIR/sppas/src/$1" -v -t "$SPPAS" -p "test_*.py" 2>> $TEMP
    echo " ================================================ " >> $TEMP
    echo >> $TEMP

    local error=`grep -c '... ERROR' $TEMP`
    local fail=`grep -c '... FAIL' $TEMP`
    echo " ... ... $error error(s) and $fail test(s) failed."

    cat $TEMP >> diagnosis.log
    echo >> diagnosis.log
    rm $TEMP
}


# Use unittest to check the API
function fct_test_api {
    echo -e "${BROWN} - Unittest of the API.${NC}"

    echo >> diagnosis.log
    echo "##########  ${PROGRAM_NAME} API Diagnosis - $TODAY #########" >> diagnosis.log
    echo >> diagnosis.log

    fct_perform_unittest "anndata"
    fct_perform_unittest "annotations"
    fct_perform_unittest "audiodata"
    fct_perform_unittest "calculus"
    fct_perform_unittest "presenters"
    fct_perform_unittest "resources"
    fct_perform_unittest "plugins"
    fct_perform_unittest "structs"
    fct_perform_unittest "utils"

    echo " ######### ############################ ######### " >> diagnosis.log
    echo >> diagnosis.log
}


# Main function for the diagnosis
function fct_diagnosis {
    fct_echo_title "${PROGRAM_NAME} - Diagnosis"
    fct_test_api
    fct_test_annotations
    echo "Check out the diagnosis.log file for details."
}



# ===========================================================================
# DOCUMENTATION
# ===========================================================================

# Generate a new version of the API manual
function fct_api_manual {
    fct_echo_title "${PROGRAM_NAME} - API Manual"

    if [ -e web/api ] ; then
        rm -rf web/api;
    fi

    # test if sphinx is ok.
    type sphinx-build >& /dev/null
    if [ $? -eq 1 ] ; then
        echo -e "${RED}sphinx-build is missing. Please, install it and try again.${NC}"
        return 1
    fi

    # OK... generate the API manual
    sphinx-build -w sphinx-doc/sphinx.log -b html -d sphinx-doc/_build/doctrees sphinx-doc web/api
    echo " The API reference manual of the web directory was updated."
    echo " ... Check out the sphinx-doc/sphinx.log file for details."

    rm -rf sphinx-doc/_build/*
}



# ===========================================================================
# TUTORIALS
# ===========================================================================

# Return a string indicating the list of files for a folder of the
# documentation
# Parameters:
#  $1: directory of the documentation
#  $2: folder name (without path) of the documentation
function fct_get_md_idx {

    # Get all files mentioned in the idx
    local f="`cat $1/$2/$2.idx`"

    # Add its path to each file name
    local mdfiles="`for i in $f; do echo "$1/$2/"$i; done`"

    # return the list of files
    echo $mdfiles
}


# Return the list of folders of the documentation
# Parameters:
#  $1: directory of the documentation
function fct_get_docfolders {

    local docfolders="`cat $1/markdown.idx`"
    echo $docfolders
}


# Return a string indicating the list of files for the documentation
# Parameters:
# - $1: directory with the documentation
function fct_get_all_md {

    local files=""
    # take a look if an header is existing (the title/author/date of the doc)
    if [ -e "$1/header.md" ] ; then
        local files="$1/header.md";
    else
        local files=""
    fi
    # get the list of all indexed folders in the documentation directory
    local folders=$(fct_get_docfolders $1)
    # get all indexed files of each folder
    for folder in $folders;
    do
        files="$files $(fct_get_md_idx $1 $folder)"
    done

    # return the list of files we just created
    echo $files
}

# Generate a new version of the tutorials
function fct_sppas_tuto {

    fct_echo_title "${PROGRAM_NAME} - Tutorials"

    cat tuto/tutorial_header.html > web/tutorial.html
    echo "<h1>In-line tutorials</h1>" >> web/tutorial.html

    # An HTML file is generated for each md file of each folder of the tutorial
    i=1
    local folders=$(fct_get_docfolders tuto)
    for folder in $folders;
    do
        foldername=`echo $folder | cut -f1 -d';'`
        foldertitle=`echo $folder | cut -f2 -d';' | sed -e 's/_/ /g'`
        
        echo "<h3>Tutorial $i: $foldertitle</h3>" >> web/tutorial.html
        
        echo " ... $folder"
        local files=$(fct_get_md_idx tuto $foldername)
        
        for file in $files;
        do 
            echo " ... ... $file"
            outfile=`basename $file .md`
            pandoc -s --mathjax -t dzslides --css web/etc/styles/tuto.css --slide-level=2 -H tuto/include-scripts.txt tuto/header.md $file -o toto.html

            cat toto.html | sed -e 's/>[ ]*</>\n</g' |\
                sed -e 's/<section>/<section class="title">/' |\
                sed -e "s/autoplay: \"1\"/autoplay: \"0\"/" |\
                awk 'BEGIN{instyle=0;infigure=0}\
                /<style>/{instyle=1}\
                /<\/style>/{instyle=0;infigure=0}\
                /figure /{if (instyle==1) infigure=1;next}\
                {if (infigure==0) print;}' |\
                awk 'BEGIN{infigure=0}\
                /<figure>/{infigure=1}\
                /<\/figure>/{infigure=0}\
                /<embed /{if (infigure==0) {print "<figure>\n",$0,"\n</figure>"; next;}}\
                /<img /{if (infigure==0) {print "<figure>\n",$0; infigure=2; next;} else {print; next;}}\
                {if (infigure==2) {print "\n</figure>\n";infigure=0;}; print}' |\
                awk 'BEGIN{infigure=0}\
                /<figure>/{infigure=1}\
                /<\/figure>/{infigure=0}\
                /<embed /{if (infigure==1) {if (match($0,".wav")){gsub("<embed ", "<audio ", $0); gsub("/>", " controls> </audio>",$0);} \
                                            else {gsub("<embed ", "", $0);gsub("/>","",$0); lab=$0; vid=$0; sub(".mp4",".vtt",lab); $0="<video width=480 controls " vid "><track label=\"English\" kind=\"subtitles\" srclang=\"en\" " lab " default></video>";}}}\
                {print}'  > web/tutorial_${outfile}.html

            rm toto.html
            echo '<p><a href="tutorial_'${outfile}'.html">'`head -n1 $file | sed -e "s/[#]*//"`'</a></p>' >> web/tutorial.html
        done
        i=$((i+1))
        echo '<p><br></p>' >> web/tutorial.html

    done
    echo '<p><br><br></p>' >> web/tutorial.html
    cat tuto/tutorial_footer.html >> web/tutorial.html

}


# ===========================================================================
# PACKAGE
# ===========================================================================

function fct_package {
    fct_echo_title "${PROGRAM_NAME} - Packaging"

    # Create the package

    local packagename=`pwd`/${PROGRAM_NAME}-${PROGRAM_VERSION}-${TODAY}.zip
    pushd $PROGRAM_DIR
    zip -q -r $packagename sppas.bat sppas.command bin etc documentation sppas resources samples scripts *.txt
    if [ "$?" != 0 ]; then
        echo -e "${RED}No package created!${NC}"
        popd
        return 1
    else
        popd
        echo "  The file" $packagename "has been created."
    fi

}

# ===========================================================================
# CLEAN
# ===========================================================================

function fct_clean_all {
    fct_echo_title "${PROGRAM_NAME} - Clean all contents"
    fct_clean_temp
    fct_clean_sppas
    fct_clean_test
    echo " The sppas folder now is clean!"

 }

# ===========================================================================
# unused
# ===========================================================================

function fct_uml_diagrams {
    echo -e "${BROWN} - $PROGRAM_NAME UML diagrams${NC}"
    # test if yuml is ok. https://github.com/wandernauta/yuml/
    type $BIN_DIR/yuml >& /dev/null
    if [ $? -eq 1 ] ; then
        # test if suml is ok. https://pypi.python.org/pypi/scruffy
        type suml >& /dev/null
        if [ $? -eq 1 ] ; then
            echo -e "${RED}None of yuml or suml are working! Please, install at least one of them and try again.${NC}"
            return 1
        else
            suml --png --class -i web/etc/figures/src/anndata.yuml -o web/etc/figures/anndata.png
        fi
    else
        cat etc/figures/src/anndata.yuml | $BIN_DIR/yuml -f png -t class -s plain --scale 42 -o web/etc/figures/anndata.png
    fi

}

# ===========================================================================
# MAIN
# ===========================================================================

fct_test_running "sppas.command"   # Is SPPAS currently running?
fct_test_running "annotation.py"   # Is SPPAS currently running?
fct_clean_temp            # Clean the current directory
fct_test_nb_args "$#"     # Test if this scripts has the expected number of arguments
fct_get_args "$@"         # Fix options from arguments
fct_echo_header           # Print the header message on stdout

if [ $DO_DIAGNOSIS == "True" ]; then fct_diagnosis; fi
if [ $DO_MANUAL == "True" ]; then fct_api_manual; fi
if [ $DO_TUTO == "True" ]; then fct_sppas_tuto; fi
if [ $DO_PACKAGE == "True" ]; then fct_clean_sppas; fct_package; fi
if [ $DO_CLEAN == "True" ]; then fct_clean_all; fi

fct_clean_test
fct_echo_title "Terminated."

# ===========================================================================
