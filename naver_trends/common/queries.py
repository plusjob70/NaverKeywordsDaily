# return : keyword, device_type, latest_date
find_latest_date = '''
                        SELECT 
                            keyword, {sep}, max(date) AS latest_date
                        FROM
                            {project}.{dataset}.{table}
                        GROUP BY
                            keyword, {sep}
                  '''