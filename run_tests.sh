green=`tput setaf 2`
cyan=`tput setaf 6`
reset=`tput sgr0`
find tests -name '*tests.py' -print0 |
    while IFS= read -r -d '' line; do
        echo "${line}"
        if [[ $line = "tests/filter_tests.py" ]]
        then
            echo "${green} Running tests for ${line} ${reset}"
            python3 -m coverage run "$line"
            echo "${cyan} Coverage Report for ${line}"
            python3 -m coverage report -m visualization/filtering/filter_options.py
        elif [[ $line = "tests/signal_loading_tests.py" ]]
        then
            echo "${green} Running tests for ${line} ${reset}"
            python3 -m coverage run "$line"
            echo "${cyan} Coverage Report for ${line}"
            python3 -m coverage report -m visualization/signal_loading/channel_options.py
            python3 -m coverage report -m visualization/signal_loading/channel_info.py
        elif [[ $line = "tests/plot_tests.py" ]]
        then
            echo "${green} Running tests for ${line} ${reset}"
            python3 -m coverage run "$line"
            echo "${cyan} Coverage Report for ${line}"
            python3 -m coverage report -m visualization/plot.py
        else
            echo "TODO: add other tests here"
            # coverage report
        fi
    done
echo "${reset}"
