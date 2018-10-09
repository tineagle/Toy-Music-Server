<?php
    header('Content-Type: application/json');

    // Serve GET requests only
    $_SERVER['REQUEST_METHOD'] === 'GET' or exit("{}");

    // Only care about certain query fields
    $query = new Query('q', 'title', 'artist', 'album');

    // Connect to server
    $connection = new PDO(
        'mysql:host=localhost;dbname=media',
        'http'
    );

    // Prepare and send statement
    $statement = $connection->prepare($query->query);
    $statement->execute($query->values);

    // Fetch rows
    $data = $statement->fetchAll(PDO::FETCH_ASSOC);
    
    // Convert and return JSON
    echo json_encode($data);
    return;

    // ------------------------------------

    class Query {
        var $values = [];
        var $query = '';

        function __construct($query_key, ...$keys) {
            // Get select query string
            $select_field = new SelectField($query_key);

            // Get subqueries that compose the where clause
            $subqueries = array_map(function($key) { 
                return new SubQuery($key);
            }, $keys);
            
            // Combine subarrays of values
            foreach($subqueries as $subquery) {
                $this->values = array_merge($this->values, $subquery->values);
            }
            
            // Combine subarrays of where clauses
            $subwheres = [];
            foreach($subqueries as $subquery) {
                if($subquery->where) {
                    array_push($subwheres, $subquery->where);
                }
            }

            // Join into single where clause across AND
            $where = '';
            if ($subwheres) {
                $where = 'WHERE '.join(' AND ', $subwheres);
            }

            // Note: first SELECT field is DISTINCT
            $this->query = 'SELECT DISTINCT '.$select_field->select.' FROM music '.$where;
        }
    }

    class SelectField {
        var $select = '*';

        function __construct($key) {
            // Check for field
            if (!array_key_exists($key, $_GET)) {
                return;
            }

            // Convert single value field to array
            $values = is_array($_GET[$key]) ? $_GET[$key] : [$_GET[$key]];

            $subselects = [];
            // Filter array to allowed values
            foreach ($values as $value) {
                if (in_array($value, ['artist', 'album', 'title'])) {
                    array_push($subselects, $value);
                }
            }
            // Join to select format
            $this->select = join(', ', $subselects);
        }
    }

    class SubQuery {
        var $values = [];
        var $where = '';

        function __construct($key) {
            // Check for field
            if (!array_key_exists($key, $_GET)) {
                return;
            }

            // Convert single value field to array
            $this->values = is_array($_GET[$key]) ? $_GET[$key] : [$_GET[$key]];

            // Convert to same-sized array of '$key LIKE ?'
            $subwheres = array_map(function($value) use ($key) {
                return "$key LIKE ?";
            }, $this->values);

            // Join into where clause across OR, skipping if empty
            if ($subwheres) {
                $this->where = '('.join(' OR ', $subwheres).')';
            }
        }
    }
?>