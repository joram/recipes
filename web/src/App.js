import React from 'react';
import './App.css';
import {Grid, List, Menu, Segment, Sidebar} from 'semantic-ui-react'


class Ingredient extends React.Component {
  render(){
    return <Menu.Item as='a'>
      {this.props.ingredient.name}
      <br/>
      ({this.props.ingredient.spoken})
    </Menu.Item>

  }
}


class Ingredients extends React.Component {
  render(){

    let i = 0;
    let ingredients = []
    this.props.ingredients.forEach(ingredient => {
      ingredients.push(<Ingredient ingredient={ingredient} key={"ingredient_"+i}/>)
      i += 1
    })

    return (<Sidebar
      as={Menu}
      icon='labeled'
      vertical
      visible={true}
    >
      <br/>
      <List.Header><h3>Ingredients</h3></List.Header>
      {ingredients}
    </Sidebar>)
  }
}


class Instructions extends React.Component {
  render() {
    let i = 1;
    let steps = []
    this.props.instructions.forEach(step => {
      steps.push(<List.Item key={"instruction_"+i}>

        <List.Content>
          {i}) {step}
        </List.Content>
      </List.Item>)
      i += 1;
    })
    return <List divided relaxed>
      <List.Header><h3>Instructions</h3></List.Header>
      {steps}
    </List>
  }
}


class App extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      error: null,
      isLoaded: false,
      recipe: null
    };
  }

  componentDidMount() {
    let host = "https://recipes.oram.ca"
    // if(window.location.hostname==="localhost")
    //   host = "http://localhost:5000"

    fetch(`${host}/api/v0/recipe/recipe_da2ddeea30c98822dbfa6182dc4f465a100e919d438691913bc8a1c7`)
    .then(res => res.json())
    .then(recipe => {
      this.setState({
        isLoaded: true,
        recipe: recipe
      });
    })
  }

  render(){
    let ingredients = [];
    let instructions = [];
    if (this.state.recipe !== null){
      ingredients = this.state.recipe.ingredients
      instructions = this.state.recipe.instructions
    }
    console.log(this.state.recipe)

    return <div className="App">

      <Grid centered columns={2}>
          <Grid.Column>
              <Ingredients ingredients={ingredients} />
              <Segment>
                 <Instructions instructions={instructions} />
              </Segment>
          </Grid.Column>
      </Grid>
    </div>
  }
}

export default App;
