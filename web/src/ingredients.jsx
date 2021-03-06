import React from "react";
import {Divider, Grid, List, Segment} from "semantic-ui-react";
import {Link, withRouter} from "react-router-dom";


class Ingredients extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            meta: {
              tags: [],
              ingredients: [],
            },
            num_columns: Math.floor(window.innerWidth/200),
            columns: [],
        };
    }

    updateDimensions = () => {
        let state = this.state
        let old_num_columns = state.num_columns
        state.num_columns = Math.floor(window.innerWidth/200)
        if(old_num_columns !== state.num_columns) {
            let cols = this.calculateColumns(state.meta.ingredients)
            state.columns = cols.columns
            state.num_columns = cols.num_columns
        }
        this.setState(state);
    }

    componentWillUnmount() {
        window.removeEventListener('resize', this.updateDimensions.bind(this));
    }

    componentDidMount() {
        window.addEventListener('resize', this.updateDimensions.bind(this));
        let host = "https://recipes.oram.ca"
        if(window.location.hostname==="localhost")
          host = "http://localhost:5000"
        fetch(`${host}/api/v0/meta`)
        .then(res => res.json())
        .then(meta => {
            let cols = this.calculateColumns(meta.ingredients)
          this.setState({
            meta: meta,
            num_columns: cols.num_columns,
            columns: cols.columns,
          });
        })
    }

    calculateColumns(ingredients){
        let firstChar = ""
        let items = []
        let i = 0;
        ingredients.sort().forEach(ingredient => {
            if(ingredient[0] !== firstChar) {
                firstChar = ingredient[0]
                items.push(<List.Item key={`ingr_${firstChar}+${i}`}>
                    {firstChar}
                    <Divider />
                    </List.Item>
                )
                i += 1
            }

            items.push(<List.Item key={`tag_${ingredient}`}>
                <Link to={`/search?ingredient=${ingredient}`}>{ingredient}</Link>
            </List.Item>
            )
        })

        let columns = []
        let num_columns = Math.floor(window.innerWidth/200)
        if(num_columns > 6)
            num_columns = 6
        let rows_per_column = items.length/num_columns
        let j;
        for (i=0,j=items.length; i<j; i+=rows_per_column) {
            let column_list = items.slice(i,i+rows_per_column);
            columns.push(<Grid.Column key={`tags_col_${i}`}>
                <List key={`tag_list_${i}`}>{column_list}</List>
            </Grid.Column>)
        }
        return {
            columns:columns,
            num_columns: num_columns,
        }
    }

    render() {
        return <Segment basic>
            <Grid columns={this.state.num_columns} divided>
                {this.state.columns}
            </Grid>
        </Segment>
    }
}

export default withRouter(Ingredients);