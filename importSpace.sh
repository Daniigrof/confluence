#!/bin/bash

ADMIN_USERNAME=admin
ADMIN_PASSWORD='Wiz2025$1!'
BUILD_INDEX=true # if you want to trigger a reindex immediately after the space import (false if you don't)
CONFLUENCE_BASE_URL='https://rsconf.realsenseai.com'
SPACE_FILE_NAME="Confluence-space-export-SW1-2025-04-01-07-18-53-710.xml_fixed.zip" # here you put only the export file name, without any path (it needs to reside inside the <confluence-shared-home/restore directory)
TASK_ID_FILE=/tmp/space_import_task.session
CONFLUENCE_COOKIE_FILE=/tmp/space_import.cookie
RESPONSE_FILE=/tmp/response.txt
STATUS_REFRESH_INTERVAL=0.5 # refresh rate (in seconds) for the space import status request

overwrite() { 
    echo -e "\r\033[1A\033[0K$@"; 
}

get_atl_token_session_cookie() {
    # Removing temporary token/cookie and task ID files from previous execution of the script
    rm -f ${TASK_ID_FILE} ${CONFLUENCE_COOKIE_FILE};

    echo "[ $(date) ] INFO Authenticating with Confluence ..."
    AUTH_HTTP_RESPONSE=$(curl -o ${RESPONSE_FILE} -w "%{http_code}" -s -c ${CONFLUENCE_COOKIE_FILE} -u ${ADMIN_USERNAME}:${ADMIN_PASSWORD} ${CONFLUENCE_BASE_URL}'/users/viewmyprofile.action')

    if [ $? -ne 0 ] || [ ${AUTH_HTTP_RESPONSE} -ne 200 ] ; then
        echo "[ $(date) ] ERROR Authentication failed: [HTTP response: ${AUTH_HTTP_RESPONSE}]. Check [${RESPONSE_FILE}] for details."
        exit 1
    else
        echo "[ $(date) ] INFO Retrieving the ATL_TOKEN ..."
        ATLASSIAN_TOKEN=$(grep "atlassian-token" ${RESPONSE_FILE} | awk -F"\"" '{print $6}')

        if [[ -z "${ATLASSIAN_TOKEN}" ]] ; then
            echo "[ $(date) ] ERROR ATL_TOKEN retrieval failed."
            exit 1
        else
            space_import;
        fi
    fi
}

space_import() {
    echo "[ $(date) ] INFO Starting the space import [file: <shared_home>/restore/${SPACE_FILE_NAME}] [index rebuild post-import: ${BUILD_INDEX}] ..."
    IMPORT_HTTP_RESPONSE=$(curl -o ${TASK_ID_FILE} -w "%{http_code}" -s -L -b ${CONFLUENCE_COOKIE_FILE} ${CONFLUENCE_BASE_URL}'/admin/restore-local-file.action' \
      -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' \
      -H 'Content-Type: application/x-www-form-urlencoded' \
      -H 'Origin: '${CONFLUENCE_BASE_URL} \
      -H 'Connection: keep-alive' \
      -H 'Referer: '${CONFLUENCE_BASE_URL}'/admin/backup.action' \
      --data 'atl_token='${ATLASSIAN_TOKEN}'&localFileName='${SPACE_FILE_NAME}'&buildIndexLocalFileRestore='${BUILD_INDEX}'&edit=Import')

    if [ $? -ne 0 ] || [ ${IMPORT_HTTP_RESPONSE} -ne 200 ] ; then
        echo "[ $(date) ] ERROR Space import failed: [HTTP response: ${IMPORT_HTTP_RESPONSE}]. Check [${TASK_ID_FILE}] for details."
        exit 1
    else
        TASK_ID=$(grep "ajs-taskId" ${TASK_ID_FILE} | awk -F"\"" '{print $4}')
        ERROR_MSG=$(perl -ne 'print if /<div class="aui-message aui-message-error closeable">/../<\/div>/' ${TASK_ID_FILE} | sed 's/<[^>]*>//g' | awk 'NF' | paste -d " "  - - | tr -s " ")

        if [[ ! -z "${ERROR_MSG}" ]] ; then
            echo "[ $(date) ] ERROR Import failed: [${ERROR_MSG}]"
            exit 1
        else
            if [[ -z "${TASK_ID}" ]] ; then
                echo -e "[ $(date) ] INFO TASK_ID was not captured. Check Confluence logs [atlassian-confluence.log] file to follow the space import progress."
            else
                echo
                import_status;
            fi
        fi
    fi

    echo "[ $(date) ] Space import finished in [${elapsed_time}] seconds!"
    exit 0
}

import_status() {
    percentage_complete=0
    while [ ${percentage_complete} -lt 100 ] ; do
        TASK_STATUS=$(curl -L -b ${CONFLUENCE_COOKIE_FILE} ${CONFLUENCE_BASE_URL}'/rest/api/longtask/'${TASK_ID} -H 'Accept: */*' 2>/dev/null)
        percentage_complete=$(echo "${TASK_STATUS}" | grep -Eo 'percentageComplete.+[0-9]{1,}' | cut -d ":" -f 2 | cut -d "," -f 1)
        status=$(echo "${TASK_STATUS}" | grep -Eo 'translation.+' | cut -d ":" -f 2 | cut -d "," -f 1 | tr -d "\"")
        elapsed_time_ms=$(echo "${TASK_STATUS}" | grep -Eo 'elapsedTime.+[0-9]{1,}' | cut -d ":" -f 2 | cut -d "," -f 1)
        elapsed_time=$(printf %.$2f $(awk "BEGIN { printf "${elapsed_time_ms}/1000" }";))

        overwrite "Space import status: [${status/./}] [${percentage_complete}%]"
        sleep ${STATUS_REFRESH_INTERVAL}
    done
}

get_atl_token_session_cookie;
