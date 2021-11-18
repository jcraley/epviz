#!/bin/sh
red=`tput setaf 1`
green=`tput setaf 2`
reset=`tput sgr0`

# Run pylint over all of the files
echo "${red}-----------------------------------${reset}"
echo "${red}-----------RUNNING PYLINT----------${reset}"
echo "${red}-----------------------------------${reset}"

echo "${red} Running pylint for edf_saving ${reset}"
echo "${green} anonymizer.py ${reset}"
python3 -m pylint visualization/edf_saving/anonymizer.py

echo "${green} saveEdf_info.py ${reset}"
python3 -m pylint visualization/edf_saving/saveEdf_info.py

echo "${green} saveEdf_options.py ${reset}"
python3 -m pylint visualization/edf_saving/saveEdf_options.py

echo "${red}----------------------------------${reset}"
echo "${red} Running pylint for filtering ${reset}"

echo "${green} filter_options.py ${reset}"
python3 -m pylint visualization/filtering/filter_options.py

echo "${red}----------------------------------${reset}"
echo "${red} Running pylint for image_saving ${reset}"

echo "${green} saveImg_options.py ${reset}"
python3 -m pylint visualization/image_saving/saveImg_options.py

echo "${green} saveTopoplot_options.py ${reset}"
python3 -m pylint visualization/image_saving/saveTopoplot_options.py

echo "${red}----------------------------------${reset}"
echo "${red} Running pylint for predictions ${reset}"
echo "${green} pred_info.py ${reset}"
python3 -m pylint visualization/predictions/prediction_info.py

echo "${green} pred_options.py ${reset}"
python3 -m pylint visualization/predictions/prediction_options.py

echo "${red}----------------------------------${reset}"
echo "${red} Running pylint for preprocessing ${reset}"

echo "${green} edf_loader.py ${reset}"
python3 -m pylint visualization/preprocessing/edf_loader.py

echo "${red}----------------------------------${reset}"
echo "${red} Running pylint for signal_loading ${reset}"
echo "${green} channel_info.py ${reset}"
python3 -m pylint visualization/signal_loading/channel_info.py

echo "${green} channel_options.py ${reset}"
python3 -m pylint visualization/signal_loading/channel_options.py

echo "${green} color_options.py ${reset}"
python3 -m pylint visualization/signal_loading/color_options.py

echo "${green} organize_channels.py ${reset}"
python3 -m pylint visualization/signal_loading/organize_channels.py

echo "${red}----------------------------------${reset}"
echo "${red} Running pylint for spectrograms ${reset}"

echo "${green} spec_options.py ${reset}"
python3 -m pylint visualization/spectrogram_window/spec_options.py

echo "${red}----------------------------------${reset}"
echo "${red} Running pylint for signal stats ${reset}"

echo "${green} signalStats_info.py ${reset}"
python3 -m pylint visualization/signal_stats/signalStats_info.py

echo "${green} signalStats_options.py ${reset}"
python3 -m pylint visualization/signal_stats/signalStats_options.py

echo "${red}----------------------------------${reset}"
echo "${red} Running pylint for utils and plot.py ${reset}"

echo "${green} plot_utils.py ${reset}"
python3 -m pylint visualization/plot_utils.py

echo "${green} plot.py ${reset}"
python3 -m pylint visualization/plot.py

echo "${red}----------------------------------${reset}"

echo "${reset}"
