#include <iostream>

class Circle {
	public:
		double radius;
		std::string color;
	
		Circle(double radius, std::string color) {
			this->radius = radius;
			this->color = color;
		}
	
		double getArea() {
			return 3.14 * radius * radius;
		}
	
		void setRadius(double radius) {
			this->radius = radius;
		}
	
		void setColor(std::string color) {
			this->color = color;
		}
};

int main() {
    Circle circle(5.0, "red");

    std::cout << "The circle's area is: " << circle.getArea() << std::endl;

    circle.setRadius(10.0);
    circle.setColor("blue");

    std::cout << "The circle's radius is now: " << circle.radius << std::endl;
    std::cout << "The circle's color is now: " << circle.color << std::endl;

    return 0;
}
