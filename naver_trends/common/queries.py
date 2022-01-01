# return : keyword, device_type, latest_date
find_latest_date = '''
                    SELECT 
                        keyword, device_type, max(date) AS latest_date
                    FROM
                        {}.{}.{}
                    GROUP BY
                        keyword, device_type
                    '''